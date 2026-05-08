# -*- coding: utf-8 -*-
"""Kredit, Zinsen, Forderungen und Insolvenzen."""

from __future__ import print_function

from dataclasses import dataclass, field
from .money import Q_VALUES, vector_from_value, vector_value
from .utils import clamp, safe_div, EPS


@dataclass
class Loan:
    loan_id: str
    lender_id: str
    borrower_id: str
    principal_zw: float
    q: int
    interest_rate: float
    term: int
    remaining_term: int
    purpose: str
    remaining_principal_zw: float
    accrued_interest_zw: float = 0.0
    defaulted: bool = False
    restructured: int = 0

    def accrue(self):
        if self.defaulted:
            return 0.0
        interest = self.remaining_principal_zw * self.interest_rate
        self.accrued_interest_zw += interest
        self.remaining_term -= 1
        return interest

    def due_value(self):
        if self.defaulted:
            return 0.0
        # Zinsen periodisch, Hauptbetrag am Laufzeitende.
        due = self.accrued_interest_zw
        if self.remaining_term <= 0:
            due += self.remaining_principal_zw
        return max(0.0, due)


class CreditSystem(object):
    def __init__(self, id_generator):
        self.id_generator = id_generator
        self.loans = []
        self.defaulted_loans = []
        self.new_credit_zw = 0.0
        self.repaid_zw = 0.0
        self.default_losses_zw = 0.0

    def reset_period(self):
        self.new_credit_zw = 0.0
        self.repaid_zw = 0.0
        self.default_losses_zw = 0.0

    def choose_credit_coin(self, purpose):
        if purpose == "working_capital":
            return 5
        if purpose == "input_purchase":
            return 10
        if purpose == "wage_bridge":
            return 11
        if purpose == "capital_investment":
            return 18
        if purpose == "automation":
            return 19
        if purpose == "public_deficit":
            return 16
        if purpose == "household_emergency":
            return 1
        return 10

    def loan_rate(self, bank, borrower, q, base_rate=0.015):
        risk = 1.0 - bank.risk_score(borrower)
        debt_pressure = safe_div(borrower.wallet.debt_value(), borrower.wallet.positive_value() + 1.0, 1.0)
        q_complexity = Q_VALUES[q] / 4.0
        rate = base_rate + 0.045 * risk + 0.012 * debt_pressure + 0.018 * q_complexity
        if q in (18, 19, 20):
            rate += 0.010
        return clamp(rate, 0.005, 0.18)

    def grant_loan(self, bank, borrower, amount_zw, purpose, term=12, base_rate=0.015):
        amount_zw = float(amount_zw)
        if amount_zw <= EPS or getattr(borrower, "bankrupt", False):
            return None
        q = self.choose_credit_coin(purpose)
        score = bank.risk_score(borrower)
        max_amount = max(2.0, (bank.wallet.positive_value() + 25.0) * (0.08 + 0.18 * bank.risk_appetite) * score)
        if amount_zw > max_amount:
            amount_zw = max_amount
        if amount_zw <= EPS:
            return None
        rate = self.loan_rate(bank, borrower, q, base_rate=base_rate)
        qty = amount_zw / Q_VALUES[q]
        # Bank zahlt aus; bei systemischer Kreditvergabe darf die Bank selbst negative Positionen tragen.
        bank.wallet.transfer_vector_to(borrower.wallet, {q: qty}, allow_debt=True)
        borrower.receive_value(amount_zw)
        bank.spend_value(amount_zw)
        loan = Loan(
            loan_id=self.id_generator.new("L"),
            lender_id=bank.id,
            borrower_id=borrower.id,
            principal_zw=amount_zw,
            q=q,
            interest_rate=rate,
            term=int(term),
            remaining_term=int(term),
            purpose=purpose,
            remaining_principal_zw=amount_zw,
        )
        self.loans.append(loan)
        bank.loan_book.append(loan.loan_id)
        self.new_credit_zw += amount_zw
        return loan

    def service_loans(self, agents_by_id, event_log=None, period=0):
        active = []
        for loan in self.loans:
            if loan.defaulted:
                self.defaulted_loans.append(loan)
                continue
            borrower = agents_by_id.get(loan.borrower_id)
            lender = agents_by_id.get(loan.lender_id)
            if borrower is None or lender is None:
                loan.defaulted = True
                self.defaulted_loans.append(loan)
                continue
            loan.accrue()
            due = loan.due_value()
            if due <= EPS:
                active.append(loan)
                continue
            # Schuldner zahlt. Bei kurzfristigem Mangel entsteht nicht automatisch neue Schuld,
            # sondern Restrukturierung oder Ausfall.
            available = borrower.wallet.positive_value()
            if available >= due * 0.98:
                paid = borrower.wallet.pay_value_to(lender.wallet, due, debt_q=loan.q, allow_debt=False)
                borrower.spend_value(paid)
                lender.receive_value(paid)
                self.repaid_zw += paid
                if loan.remaining_term <= 0:
                    loan.remaining_principal_zw = 0.0
                    loan.accrued_interest_zw = 0.0
                    continue
                else:
                    loan.accrued_interest_zw = 0.0
                    active.append(loan)
            else:
                # Teilzahlung, dann Restrukturierung. Bei wiederholtem Scheitern: Default.
                paid = 0.0
                if available > 0.25:
                    paid = borrower.wallet.pay_value_to(lender.wallet, min(available, loan.accrued_interest_zw), debt_q=loan.q, allow_debt=False)
                    borrower.spend_value(paid)
                    lender.receive_value(paid)
                    self.repaid_zw += paid
                    loan.accrued_interest_zw = max(0.0, loan.accrued_interest_zw - paid)
                loan.restructured += 1
                loan.remaining_term += 3
                loan.interest_rate = clamp(loan.interest_rate * 1.12, 0.005, 0.22)
                if loan.restructured >= 4 or getattr(borrower, "bankrupt", False):
                    loss = loan.remaining_principal_zw + loan.accrued_interest_zw
                    loan.defaulted = True
                    self.default_losses_zw += loss
                    if hasattr(lender, "default_losses"):
                        lender.default_losses += loss
                    # Bank bekommt negative Kapitalmünze für Fehllenkung.
                    lender.wallet.add_coin(10, -loss / Q_VALUES[10] * 0.20)
                    if event_log is not None:
                        event_log.add(period, "default", "Kreditausfall %s über %.2f ZW" % (loan.loan_id, loss), {
                            "borrower": borrower.id,
                            "lender": lender.id,
                            "purpose": loan.purpose,
                        })
                    self.defaulted_loans.append(loan)
                else:
                    active.append(loan)
        self.loans = active

    def outstanding_value(self):
        return sum(l.remaining_principal_zw + l.accrued_interest_zw for l in self.loans if not l.defaulted)

    def by_purpose(self):
        out = {}
        for l in self.loans:
            out[l.purpose] = out.get(l.purpose, 0.0) + l.remaining_principal_zw
        return out
