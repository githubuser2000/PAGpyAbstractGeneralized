T = Topologie.indiskrete_topologie({1, 2, 3})
T.add_offene_menge({1}, automatisch_erweitern=True)
print(T.offene_mengen)
