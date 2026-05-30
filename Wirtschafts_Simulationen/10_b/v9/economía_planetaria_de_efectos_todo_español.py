#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
from __future__ import annotations
'Simulación de economía planetaria de efectos\n\nSimulación completa compatible con PyPy3 de una economía planetaria basada en valores lógicos de verdad apilados. La economía coordina causalidad, tiempo, intensidad, existencia, potencias, efectos, sustancia, materia, diferencia, determinación, fenómenos y dirección angular en vez de precio, cantidad, valor e intercambio de cosas.'

import argparse
import csv
import json
import math
import os
import random
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Core vocabulary: stacked logical truth values
# ---------------------------------------------------------------------------

TRUTH_DIMS = (
    "causality",          # confidence that a chosen intervention actually acts on the cause
    "time",               # urgencia in time
    "intensity",          # strength/severity of the phenomenon
    "existence",          # how real/present the phenomenon is
    "potencies",          # how much solvable possibility exists
    "effects",            # expected positive systemic effect if solved
    "substance",          # input/substance availability
    "matter",             # material/infrastructure proximity
    "difference",         # gap between need and state
    "determination",      # democratically confirmed priority / social determination
    "phenomena",          # visible or reported appearance of the issue
    "angle_direction",    # alignment of the action with planetary regeneration and human freedom
)

TRUTH_WEIGHTS = {
    "causality": 0.08,
    "time": 0.12,
    "intensity": 0.12,
    "existence": 0.08,
    "potencies": 0.08,
    "effects": 0.12,
    "substance": 0.07,
    "matter": 0.07,
    "difference": 0.14,
    "determination": 0.08,
    "phenomena": 0.07,
    "angle_direction": 0.09,
}

# Domains are not "markets". They are real need/effect fields.
DOMAINS = (
    "water",
    "food",
    "energy",
    "shelter",
    "health",
    "care",
    "education",
    "mobility",
    "manufacturing",
    "storage",
    "governance",
    "knowledge",
    "resilience",
    "repair",
    "ecology",
    "waste",
)

# Sectors replace national-account categories such as agriculture, industry,
# services, state, capital formation and foreign trade. They are not markets;
# they are fields of planetary reproduction.
SECTOR_FOR_DOMAIN = {
    "water": "primary_reproduction",
    "food": "primary_reproduction",
    "energy": "infrastructure_energy",
    "shelter": "social_infrastructure",
    "health": "care_reproduction",
    "care": "care_reproduction",
    "education": "knowledge_reproduction",
    "mobility": "logistics_circulation",
    "manufacturing": "material_transformation",
    "storage": "resilience_capital",
    "governance": "institutional_coordination",
    "knowledge": "knowledge_reproduction",
    "resilience": "risk_protection",
    "repair": "circular_industry",
    "ecology": "planetary_regeneration",
    "waste": "material_difference_resolution",
}

CONSUMABLE_DOMAINS = ("water", "food", "energy")
SERVICE_DOMAINS = ("health", "care", "education", "mobility", "governance", "knowledge", "resilience")
CAPACITY_DOMAINS = ("shelter", "manufacturing", "storage")
MACRO_CAPACITY_DOMAINS = CAPACITY_DOMAINS + SERVICE_DOMAINS

# One simulation step = one month. Units are normalized person-months or
# capability-months. These are not prices and not exchange values.
NEED_PER_PERSON = {
    "water": 1.0,
    "food": 1.0,
    "energy": 1.0,
    "shelter": 1.0,   # capacity for one person
    "health": 0.22,   # average monthly health service need
    "care": 0.18,     # care load, higher for children/elders/unwell cohorts
    "education": 0.20,
    "mobility": 0.23,
    "manufacturing": 0.12,  # tools, basic industry, replacement parts
    "storage": 0.08,        # buffers, warehouses, grid/storage systems
    "governance": 0.06,     # democratic coordination and dispute resolution
    "knowledge": 0.07,      # research, open plans, technical learning
    "resilience": 0.09,     # emergency readiness and redundancy
}

# nombres de presión planetaria. Pressure > 1 means overshoot beyond safe operating space.
BOUNDARY_NAMES = (
    "climate",
    "biosphere",
    "freshwater",
    "soil",
    "pollution",
    "material_throughput",
    "energy_throughput",
)

BOUNDARY_WEIGHTS = {
    "climate": 1.3,
    "biosphere": 1.25,
    "freshwater": 1.1,
    "soil": 1.0,
    "pollution": 1.05,
    "material_throughput": 0.85,
    "energy_throughput": 0.85,
}


# ---------------------------------------------------------------------------
# Visible trade vocabulary: what is traded when there is no price/value trade
# ---------------------------------------------------------------------------

# The dimension guide is deliberately verbose. In this model a "contract" is not
# a money contract. It is a condition set for a causal effect flow: what is
# accepted, contributed, transferred, protected, limited and corrected.
DIMENSION_GUIDE = {'causality': {'name': 'Causalidad',
               'short': 'Ca',
               'question': '¿La acción toca la causa real, o solo un síntoma?',
               'contract_role': 'Fija prueba causal, estado de ensayo y deber de corrección.',
               'economic_replacement': 'sustituye la señal de precio por prueba de causa y efecto'},
 'time': {'name': 'Tiempo',
          'short': 'Ti',
          'question': '¿Qué urgencia tiene el efecto y en qué ventana debe llegar?',
          'contract_role': 'Fija plazo, vía de urgencia, duración y prioridad.',
          'economic_replacement': 'sustituye la fecha de entrega por urgencia real'},
 'intensity': {'name': 'Intensidad',
               'short': 'In',
               'question': '¿Qué fuerza tienen la necesidad, el daño, la carga o el efecto positivo?',
               'contract_role': 'Fija fuerza de despliegue, tiempo de trabajo, nivel de protección y escalada.',
               'economic_replacement': 'sustituye la disposición a pagar por fuerza del fenómeno'},
 'existence': {'name': 'Existencia',
               'short': 'Ex',
               'question': '¿El fenómeno está presente, medido, informado y verificable?',
               'contract_role': 'Fija si el contrato descansa en realidad o en supuesto.',
               'economic_replacement': 'sustituye la prueba de propiedad por prueba de existencia del estado'},
 'potencies': {'name': 'Potencias',
               'short': 'Po',
               'question': '¿Qué capacidades, reservas, herramientas y caminos posibles existen?',
               'contract_role': 'Fija si un efecto puede ocurrir ahora, en parte, o tras crear capacidad.',
               'economic_replacement': 'sustituye la rentabilidad del capital por capacidad real de transformación'},
 'effects': {'name': 'Efectos',
             'short': 'Ef',
             'question': '¿Qué consecuencias sistémicas positivas y negativas surgen?',
             'contract_role': 'Fija efecto objetivo, revisión de efectos laterales y responsabilidad.',
             'economic_replacement': 'sustituye la ganancia por efectos reales sobre personas, naturaleza e infraestructura'},
 'substance': {'name': 'Sustancia',
               'short': 'Su',
               'question': '¿Qué materia, energía, alimento, agua, conocimiento o tiempo de cuidado está disponible?',
               'contract_role': 'Fija liberación material, límites de sustancia y deber circular.',
               'economic_replacement': 'sustituye el valor de mercancía por condición material'},
 'matter': {'name': 'Materia',
            'short': 'Ma',
            'question': '¿Dónde están el lugar material y la infraestructura, y son alcanzables?',
            'contract_role': 'Fija lugar, logística, cercanía, carga de transporte y viabilidad local.',
            'economic_replacement': 'sustituye el acceso al mercado por ubicación material real'},
 'difference': {'name': 'Diferencia',
                'short': 'Di',
                'question': '¿Qué tamaño tiene la brecha entre necesidad y realidad existente?',
                'contract_role': 'Fija si debe haber acción y cuánta contradicción se resuelve.',
                'economic_replacement': 'sustituye la demanda por brecha de necesidad'},
 'determination': {'name': 'Determinación',
                   'short': 'De',
                   'question': '¿La acción está decidida socialmente, es impugnable y tiene sentido?',
                   'contract_role': 'Fija legitimidad, participación, derecho de objeción y responsabilidad.',
                   'economic_replacement': 'sustituye el poder de las partes por determinación colectiva'},
 'phenomena': {'name': 'Fenómenos',
               'short': 'Fe',
               'question': '¿Cómo aparece el estado en observación, medición e informes de personas afectadas?',
               'contract_role': 'Fija base de prueba, observación, auditoría y deber de corrección.',
               'economic_replacement': 'sustituye la observación de mercado por lógica de aparición y respuesta'},
 'angle_direction': {'name': 'Dirección angular',
                     'short': 'Án',
                     'question': '¿Hacia dónde se mueve la acción: regeneración, neutralidad, explotación o control?',
                     'contract_role': 'Fija si la acción se permite, condiciona, reconstruye o bloquea.',
                     'economic_replacement': 'sustituye la dirección de crecimiento por dirección de efecto'}}

TRADE_CATALOG = {'water': {'display_name': 'agua',
           'trade_object': 'Efecto de agua: agua potable, limpieza, tuberías, almacenamiento, protección de fuentes',
           'meant_as': 'asegurar existencia para sed, higiene, salud, agricultura y protección contra incendio o crisis',
           'products': 'agua potable, filtros, bombas, piezas de tubería, tanques, sensores de medición, unidades de limpieza',
           'workplaces': 'técnicas de agua; hidrólogas; constructoras de tuberías; ensayistas de laboratorio; brigadas de agua urgente; '
                         'protectoras de fuentes',
           'services': 'tratamiento, búsqueda de fugas, distribución urgente, prueba de calidad, mantenimiento de pozos y tuberías',
           'ecology': 'la cuenca de agua no debe vaciarse; restauración y reducción de fugas son cláusulas obligatorias',
           'climate': 'sequía, lluvia intensa y energía de bombeo se cuentan; soluciones de alto gasto energético necesitan cobertura '
                      'renovable'},
 'food': {'display_name': 'alimento',
          'trade_object': 'Efecto alimentario: calorías, nutrientes, fertilidad del suelo, semilla, tiempo de cosecha',
          'meant_as': 'reproducción corporal, salud, seguridad alimentaria local y suministro culturalmente adecuado',
          'products': 'grano, verduras, legumbres, fruta, semilla, cajas frías, cajas de almacenamiento, equipo de cocina',
          'workplaces': 'agricultoras; guardianas de semillas; procesadoras de alimentos; cocinas comunes; brigadas de agroecología',
          'services': 'planes de cultivo, cosecha, procesamiento, almacenamiento, distribución, comidas comunes, orientación nutricional',
          'ecology': 'formación de suelo, uso de agua, biodiversidad y carga tóxica son condiciones obligatorias',
          'climate': 'metano, fertilizante, transporte, enfriamiento y cultivos resistentes al clima forman la dirección angular'},
 'energy': {'display_name': 'energía',
            'trade_object': 'Efecto energético: luz, calor, impulso, estabilidad de red, carga almacenada',
            'meant_as': 'condición para suministro, comunicación, producción, cuidado, movilidad y protección ante desastre',
            'products': 'electricidad, calor, paneles solares, piezas eólicas, baterías, bombas de calor, cables, dispositivos de control',
            'workplaces': 'electricistas; planificadoras de red; mantenedoras de almacenamiento; instaladoras solares y eólicas; '
                          'cooperativas energéticas; gestoras de carga',
            'services': 'generación, distribución, desplazamiento de carga, reparación, orientación de aislamiento, prioridad de energía '
                        'urgente',
            'ecology': 'minería, uso de suelo, desmontaje y reciclaje pertenecen al contrato',
            'climate': 'porción fósil, eficiencia, renovabilidad y efecto de emisiones fijan permiso y prioridad'},
 'shelter': {'display_name': 'vivienda',
             'trade_object': 'Efecto de vivienda: protección, espacio, calor, seguridad, cercanía al suministro',
             'meant_as': 'base estable de existencia en vez de alquiler o propiedad como exclusión',
             'products': 'espacio habitacional, aislamiento, piezas de reparación, saneamiento, módulos, salas comunes',
             'workplaces': 'constructoras; renovadoras; arquitectas; cartógrafas de vacancia; técnicas de edificio; mediadoras de vivienda',
             'services': 'asignación por necesidad, mantenimiento, conversión, accesibilidad, renovación energética, cuidado vecinal',
             'ecology': 'conversión antes que obra nueva; sellado de suelo, ciclo material y verde local son cláusulas',
             'climate': 'energía de calefacción, aislamiento, protección frente a calor y emisiones incorporadas fijan dirección angular'},
 'health': {'display_name': 'salud',
            'trade_object': 'Efecto curativo: diagnóstico, tratamiento, prevención, medicina, tiempo de enfermería',
            'meant_as': 'estabilización física y mental por urgencia y no por capacidad de pago',
            'products': 'medicina, vendajes, aparatos de diagnóstico, camas, ayudas de rehabilitación, equipo de higiene',
            'workplaces': 'médicas; enfermeras; laboratorios; equipos de rescate; terapeutas; trabajadoras de prevención; técnicas médicas',
            'services': 'diagnóstico, tratamiento, urgencia, prevención, terapia, rehabilitación, educación sanitaria',
            'ecology': 'residuos médicos, demanda de agua y energía, y rutas tóxicas deben cerrarse',
            'climate': 'calor, nuevas cargas de enfermedad, resiliencia urgente e infraestructura climáticamente segura entran en tiempo e '
                       'intensidad'},
 'care': {'display_name': 'cuidados',
          'trade_object': 'Efecto de cuidado: enfermería, acompañamiento, protección, tiempo, relación, alivio',
          'meant_as': 'mantenimiento de dignidad, vida diaria, seguridad de dependencia y vínculo social',
          'products': 'ayudas de cuidado, sillas de ruedas, camas, bienes de higiene, dispositivos de asistencia, equipo accesible',
          'workplaces': 'cuidadoras; asistentes; trabajadoras sociales; brigadas de alivio familiar; acompañantes de demencia; equipos '
                        'vecinales',
          'services': 'cuidado básico, acompañamiento, cuidado infantil, cuidado de mayores, asistencia a discapacidad, servicios de '
                      'alivio',
          'ecology': 'rutas cortas y cuidado de baja materia son preferidos; residuos e higiene deben ser seguros',
          'climate': 'preparación ante calor y crisis para personas vulnerables pertenece a contratos de cuidado'},
 'education': {'display_name': 'educación',
               'trade_object': 'Efecto educativo: capacidad, juicio, conocimiento, autodirección, potencial futuro',
               'meant_as': 'desarrollo de potencias en vez de adiestramiento solo para utilidad de mercado',
               'products': 'aulas, libros, dispositivos, talleres, planes abiertos, material de aprendizaje, acceso digital',
               'workplaces': 'docentes; mentoras; responsables de taller; coordinadoras educativas; trabajadoras de lengua e inclusión',
               'services': 'clases, aprendizaje adulto, reconversión, educación cívica, laboratorios abiertos',
               'ecology': 'conocimiento ecológico, capacidad de reparación y ciclos de sustancia son contenido educativo',
               'climate': 'competencia climática, conocimiento de adaptación y gasto energético de infraestructura educativa se siguen'},
 'mobility': {'display_name': 'movilidad',
              'trade_object': 'Efecto de movimiento: acceso, transporte, cercanía, ruta de rescate, flujo de bienes',
              'meant_as': 'alcance de necesidades reales en vez de kilómetros vendidos o valor de billete',
              'products': 'bicicletas, autobuses, trenes, puntos de carga, caminos, repuestos, programas logísticos, vehículos de rescate',
              'workplaces': 'conductoras; planificadoras de rutas; reparadoras de bicicletas y trenes; logísticas; servicios de '
                            'accesibilidad; transporte de rescate',
              'services': 'transporte público, movimiento de bienes, transporte urgente, rutas escolares, viajes de cuidado, cadenas '
                          'compartidas',
              'ecology': 'uso de suelo, ruido, contaminación aérea y cortes de hábitat son condiciones del contrato',
              'climate': 'emisión por efecto de movimiento, electrificación y evitación de rutas innecesarias fijan dirección'},
 'manufacturing': {'display_name': 'fabricación',
                   'trade_object': 'Efecto de fabricación: herramientas, repuestos, capacidad de máquina, base de reparación',
                   'meant_as': 'capacidad de transformación material sin presión de ganancia ni obsolescencia artificial',
                   'products': 'herramientas, repuestos, módulos de máquina, carcasas, bombas, piezas médicas, herramientas agrícolas',
                   'workplaces': 'constructoras de máquinas; fabricantes; talleres abiertos; ensayistas de calidad; planificadoras de '
                                 'materiales; diseñadoras circulares',
                   'services': 'fabricación, conversión, fijación de normas, préstamo de herramientas, planes abiertos de producción, '
                               'control de calidad',
                   'ecology': 'material nuevo es secundario; reparabilidad, reciclaje y no toxicidad son requisitos',
                   'climate': 'intensidad energética, calor de proceso, rutas y flujo material limitan liberación'},
 'storage': {'display_name': 'almacenamiento',
             'trade_object': 'Efecto de almacenamiento: amortiguador, durabilidad, reserva de red, reserva urgente, puente temporal',
             'meant_as': 'protección frente a oscilaciones, choques y desajuste temporal entre necesidad y producción',
             'products': 'almacenes de alimentos, tanques de agua, baterías, depósitos de calor, cadenas frías, depósitos de repuestos',
             'workplaces': 'coordinadoras de almacenamiento; técnicas de almacenamiento; inspectoras de existencias; mantenedoras de frío; '
                           'logísticas urgentes',
             'services': 'almacenar, revisar vida útil, gestionar reservas, amortiguar red, priorizar en crisis',
             'ecology': 'deterioro, refrigerantes, espacio de almacén y uso de material son condiciones de sustancia y materia',
             'climate': 'almacenamiento reduce desperdicio pero puede usar energía y material; ambos entran en dirección'},
 'governance': {'display_name': 'gobierno',
                'trade_object': 'Efecto de determinación: decisión, ley, solución de conflictos, derechos, corrección de verdad',
                'meant_as': 'legitimación y corrección de errores de la economía planetaria en vez de regla automática de mercado o estado',
                'products': 'reglas, actas, registros de decisión, herramientas de privacidad, informes de auditoría, procedimientos de '
                            'conflicto',
                'workplaces': 'moderadoras; trabajadoras jurídicas; guardianas de privacidad; consejos ciudadanos; mediadoras; auditoras; '
                              'defensorías',
                'services': 'participación, procedimientos de objeción, revisión de verdad, liberación de recursos, solución de conflictos',
                'ecology': 'límites ecológicos se vigilan públicamente y no deben anularse por votación',
                'climate': 'contratos climáticos necesitan transparencia, horizonte largo y derechos contra desplazamiento o tecnocracia'},
 'knowledge': {'display_name': 'conocimiento',
               'trade_object': 'Efecto de conocimiento: investigación, planes abiertos, diagnóstico, simulación, curvas de aprendizaje',
               'meant_as': 'aumento de potencias y reducción de error de verdad',
               'products': 'planes abiertos, datos de medición, modelos, material docente, guías de construcción, protocolos de '
                           'diagnóstico',
               'workplaces': 'investigadoras; guardianas de datos; trabajadoras de simulación; bibliotecarias; transferidoras técnicas; '
                             'talleres locales de aprendizaje',
               'services': 'análisis, consejo, desarrollo, documentación, transferencia de conocimiento, revisión de errores',
               'ecology': 'el conocimiento debe revelar consecuencias de sustancia y no esconder externalización',
               'climate': 'modelos climáticos, conocimiento de adaptación y evaluación técnica son contenido central'},
 'resilience': {'display_name': 'resiliencia',
                'trade_object': 'Efecto de resiliencia: redundancia, capacidad urgente, protección de crisis, rutas de reemplazo',
                'meant_as': 'protección frente a choques, eventos climáticos, fallas de suministro y rupturas sociales',
                'products': 'reservas urgentes, redes de radio, filtros móviles de agua, energía de reserva, refugios, planes de '
                            'evacuación',
                'workplaces': 'protección ante desastre; ayuda médica; redundancia de red; análisis de riesgo; simulacros comunitarios; '
                              'logística urgente',
                'services': 'plan de crisis, simulacros, suministro urgente, construcción de redundancia, vigilancia de riesgo, '
                            'coordinación de recuperación',
                'ecology': 'la resiliencia no debe tratar la naturaleza como reserva de sacrificio; amortiguadores naturales son '
                           'infraestructura protectora',
                'climate': 'calor, inundación, sequía y fallo de cosecha elevan tiempo e intensidad y permiten redistribución más rápida'},
 'repair': {'display_name': 'reparación',
            'trade_object': 'Efecto de reparación: vida útil, reutilización, recuperación de repuestos, preservación de capacidad',
            'meant_as': 'resolución de diferencia material en vez de compra nueva y descarte',
            'products': 'repuestos, aparatos restaurados, ropa reparada, piezas de construcción, juegos de herramientas, material '
                        'recuperado',
            'workplaces': 'talleres de reparación; diseñadoras circulares; clasificadoras; mantenedoras; reparadoras de electrónica, '
                          'textil y construcción',
            'services': 'reparación, mantenimiento, diagnóstico, reacondicionamiento, recuperación material, extensión de vida útil',
            'ecology': 'reduce residuos, presión de materias primas y tóxicos; seguridad tóxica sigue siendo condición',
            'climate': 'baja emisiones incorporadas y flujo material; reparación de alto gasto energético debe valer ecológicamente'},
 'ecology': {'display_name': 'ecología',
             'trade_object': 'Efecto de regeneración: suelo, biodiversidad, equilibrio hídrico, enfriamiento, hábitat',
             'meant_as': 'base vital planetaria como trabajo económico activo, no como fondo gratuito',
             'products': 'tierras restauradas, semillas, humedales, agroforestería, verde urbano, material de protección de suelo',
             'workplaces': 'ecólogas; brigadas de restauración; guardianas de bosque y agroforestería; cuidadoras de cauces; monitoras de '
                           'biodiversidad',
             'services': 'formación de suelo, rehumectación, forestación, seguimiento de especies, restauración de cauces, planificación '
                         'de áreas frías',
             'ecology': 'esta es función ecológica básica directa; explotación no debe registrarse como regeneración',
             'climate': 'captura, enfriamiento, retención de agua y adaptación elevan dirección angular y efecto'},
 'waste': {'display_name': 'residuos',
           'trade_object': 'Resolución de diferencia de residuos: clasificación, aseguramiento tóxico, retorno, compostaje',
           'meant_as': 'residuo no es subproducto sino diferencia material visible sin resolver',
           'products': 'materiales secundarios, compost, metales separados, plásticos, unidades seguras de vertedero, material de '
                       'reparación',
           'workplaces': 'clasificadoras; recicladoras; probadoras de tóxicos; compostadoras; logísticas circulares; auditoras materiales',
           'services': 'recogida, separación, descontaminación, recuperación, reutilización, almacenamiento final seguro',
           'ecology': 'tóxicos deben mantenerse fuera de suelo, agua y cuerpos; ciclo antes que vertedero',
           'climate': 'metano, quema, transporte y nueva producción evitada fijan efecto climático'}}

CONTRACT_VALIDITY_LABELS = {'valid': 'válido', 'conditional': 'válido con condición', 'experimental': 'experimental', 'blocked': 'bloqueado y rediseñado'}
DISPLAY_DOMAIN_NAMES = {'water': 'agua',
 'food': 'alimento',
 'energy': 'energía',
 'shelter': 'vivienda',
 'health': 'salud',
 'care': 'cuidados',
 'education': 'educación',
 'mobility': 'movilidad',
 'manufacturing': 'fabricación',
 'storage': 'almacenamiento',
 'governance': 'gobierno',
 'knowledge': 'conocimiento',
 'resilience': 'resiliencia',
 'repair': 'reparación',
 'ecology': 'ecología',
 'waste': 'residuos'}
DISPLAY_SECTOR_NAMES = {'primary_reproduction': 'reproducción primaria',
 'infrastructure_energy': 'infraestructura energética',
 'social_infrastructure': 'infraestructura social',
 'care_reproduction': 'reproducción de cuidados',
 'knowledge_reproduction': 'reproducción de conocimiento',
 'logistics_circulation': 'circulación logística',
 'material_transformation': 'transformación material',
 'resilience_capital': 'capacidad de resiliencia',
 'institutional_coordination': 'coordinación institucional',
 'risk_protection': 'protección de riesgo',
 'circular_industry': 'industria circular',
 'planetary_regeneration': 'regeneración planetaria',
 'material_difference_resolution': 'resolución de diferencia material'}
DISPLAY_BOUNDARY_NAMES = {'climate': 'clima',
 'biosphere': 'biosfera',
 'freshwater': 'agua dulce',
 'soil': 'suelo',
 'pollution': 'contaminación',
 'material_throughput': 'flujo material',
 'energy_throughput': 'flujo energético'}
SCENARIO_ARG_TO_INTERNAL = {'bienes_comunes_planetarios': 'planetary_commons',
 'democracia_local': 'local_democracy',
 'control_tecnocrático': 'technocratic_control',
 'crisis_ecológica': 'ecological_crisis',
 'choque_de_escasez': 'scarcity_shock'}
SCENARIO_INTERNAL_TO_LABEL = {'planetary_commons': 'bienes comunes planetarios',
 'local_democracy': 'democracia local',
 'technocratic_control': 'control tecnocrático',
 'ecological_crisis': 'crisis ecológica',
 'scarcity_shock': 'choque de escasez'}
SCENARIO_INTERNAL_TO_ARG = {'planetary_commons': 'bienes_comunes_planetarios',
 'local_democracy': 'democracia_local',
 'technocratic_control': 'control_tecnocrático',
 'ecological_crisis': 'crisis_ecológica',
 'scarcity_shock': 'choque_de_escasez'}
DISPLAY_KIND_LABELS = {'need_acceptance': 'aceptación de necesidad',
 'contribution_offer': 'oferta de contribución',
 'planetary_transfer': 'transferencia de efecto',
 'reserve_building': 'construcción de reserva',
 'regeneration_mandate': 'mandato de regeneración'}
DISPLAY_LEGACY_LABELS = {'buy/consumption': 'compra y consumo',
 'sell/labour_supply': 'venta y oferta laboral',
 'trade/import/export': 'importación y exportación',
 'investment/stock_market': 'inversión y mercado de existencias',
 'environmental_externality': 'externalidad ambiental'}
DISPLAY_ACTION_LABELS = {'accept_effect_for_need': 'aceptar efecto para necesidad',
 'activate_causal_effect': 'activar efecto causal',
 'move_effect_to_difference': 'mover efecto hacia una diferencia',
 'build_time_buffer': 'crear amortiguador temporal',
 'restore_planetary_basis': 'restaurar base planetaria'}
UI_LABELS = {'scenario': 'escenario',
 'steps': 'pasos',
 'seed': 'semilla',
 'regions': 'regiones',
 'communes': 'comunas',
 'population': 'población',
 'wellbeing': 'bienestar',
 'unmet': 'necesidades básicas no cubiertas',
 'overshoot': 'exceso planetario',
 'truth_error': 'error de verdad',
 'autonomy': 'autonomía',
 'reproduction': 'índice de reproducción',
 'resilience': 'índice de resiliencia',
 'coordination': 'calidad de coordinación',
 'inequality': 'desigualdad de satisfacción',
 'worst_boundary': 'peor límite',
 'outputs': 'salidas',
 'score': 'puntuación',
 'priority': 'prioridad',
 'base5': 'apilamiento base cinco',
 'dimensions': 'dimensiones',
 'meaning': 'sentido',
 'what': 'lo comerciado',
 'meant': 'significa',
 'products': 'productos',
 'workplaces': 'puestos de trabajo',
 'services': 'servicios',
 'ecology': 'cláusula ecológica',
 'climate': 'cláusula climática',
 'conditions': 'condiciones contractuales',
 'from_to': 'origen destino',
 'sector': 'sector',
 'effect': 'efecto activado',
 'causal_chain': 'cadena causal',
 'direction': 'dirección angular',
 'validity': 'validez',
 'old_form': 'forma antigua',
 'new_form': 'forma nueva',
 'display': 'visualización',
 'art': 'galería de arte de caracteres',
 'contract': 'contrato',
 'question': 'pregunta',
 'action': 'acción',
 'scale': 'escala'}
UI_TEXT = {'dimension_header': 'DIMENSIONES DEL COMERCIO',
 'dimension_sub': 'Cada dimensión de verdad tiene su propio color, símbolo y papel contractual.',
 'catalog_header': 'LO COMERCIADO',
 'catalog_sub': 'Productos, puestos de trabajo, servicios, cláusulas ecológicas y cláusulas climáticas aparecen como efectos.',
 'trades_header': 'COMERCIO VISIBLE EN DIMENSIONES',
 'trades_sub': 'Vista contractual extremadamente colorida: cada dimensión tiene su propio color y una barra visible de verdad.',
 'stack_header': 'VALOR DE VERDAD APILADO',
 'stack_sub': 'El apilamiento es una firma contractual y estatal colorida, no una cifra monetaria.',
 'simulation_header': 'SIMULACIÓN DE ECONOMÍA PLANETARIA DE EFECTOS',
 'simulation_sub': 'Salida terminal colorida para economía planetaria de efectos, contratos y dimensiones de verdad',
 'base5_example': 'Ejemplo base cinco',
 'colored_stack': 'Apilamiento colorido',
 'dimensional_readout': 'Lectura dimensional',
 'importancia': 'Importante',
 'old_form': 'Forma antigua',
 'new_form': 'Forma nueva',
 'display': 'Visualización',
 'none_flows': 'No hay flujos de efecto. Aumenta los pasos o pon la visualización de comercio por encima de cero.',
 'contract': 'CONTRATO',
 'detail_heading': 'Dimensiones en detalle',
 'conditions_heading': 'Condiciones contractuales',
 'scale': 'Escala: 0 = ausente o falso | 1 = débil o latente | 2 = parcial | 3 = fuerte | 4 = crítico o muy real',
 'stack_order': 'Orden de apilamiento',
 'stack_not_money': 'El apilamiento no es dinero. Es la firma contractual y estatal de un flujo de efecto.',
 'old_form_text': 'mercancía + cantidad + precio + propiedad → compra/venta/importación/exportación',
 'new_form_text': 'causalidad + tiempo + intensidad + existencia + potencias + efectos + sustancia + materia + diferencia + determinación '
                  '+ fenómenos + dirección angular → contrato de efecto',
 'display_note': 'Cada entrada es un flujo de efecto real, no una transacción monetaria. activated_effect es unidad de efecto, no valor.',
 'stack_warning_1': 'El apilamiento se guarda como número, pero no se usa como valor ni precio.',
 'stack_warning_2': 'La puntuación ordena prioridades; las cifras individuales crean condiciones contractuales.',
 'stack_warning_3': 'Alta diferencia con baja dirección angular significa: la necesidad es real, pero la acción debe reconstruirse o '
                    'bloquearse.',
 'example_meanings': ['Causalidad=3: la causa está bien tocada.',
                      'Tiempo=3: urgente.',
                      'Intensidad=4: fenómeno muy fuerte.',
                      'Existencia=4: realmente presente, no solo afirmado.',
                      'Potencias=3: existen posibilidades de solución.',
                      'Efectos=4: alto efecto sistémico positivo.',
                      'Sustancia=2: materiales, energía o conocimiento solo están parcialmente disponibles.',
                      'Materia=3: lugar e infraestructura son suficientemente alcanzables.',
                      'Diferencia=4: la brecha de necesidad es máximamente visible.',
                      'Determinación=3: social y democráticamente bien determinada.',
                      'Fenómenos=4: fuertemente visible, informado o medido.',
                      'Dirección angular=3: la acción actúa más bien de forma regenerativa y libre.']}
OUTPUT_FILE_NAMES = {'summary': 'resumen.json',
 'timeline': 'línea_temporal.csv',
 'communes': 'comunas_finales.csv',
 'truth': 'auditoría_de_verdad.csv',
 'macro': 'cuentas_planetarias.csv',
 'flows': 'auditoría_de_flujos_de_efecto.csv',
 'dimension': 'guía_de_dimensiones.csv',
 'catalog': 'catálogo_de_comercio.csv',
 'report': 'informe_de_contratos.md',
 'manifest': 'manifiesto.md'}
UNIT_LABELS = {'billion': 'mil millones', 'million': 'millones', 'thousand': 'mil'}
LOCAL_FIELD_LABELS = {'step': 'paso',
 'kind': 'tipo',
 'legacy_term_replaced': 'término sustituido',
 'action': 'acción',
 'domain': 'dominio',
 'sector': 'sector',
 'trade_object': 'efecto comerciado',
 'meant_as': 'significa',
 'product_examples': 'productos',
 'workplace_examples': 'puestos de trabajo',
 'service_examples': 'servicios',
 'ecological_clause': 'cláusula ecológica',
 'climate_clause': 'cláusula climática',
 'contract_validity': 'validez contractual',
 'contract_conditions': 'condiciones contractuales',
 'truth_stack_score_0_4': 'puntuación de verdad de cero a cuatro',
 'truth_stack_priority_0_1': 'prioridad de verdad de cero a uno',
 'truth_stack_base5': 'apilamiento de verdad base cinco',
 'truth_stack_decimal': 'apilamiento de verdad decimal',
 'truth_stack_compact': 'apilamiento de verdad compacto',
 'dimension_meaning': 'sentido dimensional',
 'from_region': 'región de origen',
 'from_commune': 'comuna de origen',
 'to_region': 'región de destino',
 'to_commune': 'comuna de destino',
 'activated_effect': 'efecto activado',
 'causal_link': 'enlace causal',
 'direction_vector': 'vector de dirección',
 'note': 'nota',
 'region': 'región',
 'commune': 'comuna',
 'biome': 'bioma',
 'population': 'población',
 'wellbeing_proxy': 'aproximación de bienestar',
 'avg_health': 'salud media',
 'avg_education': 'educación media',
 'avg_autonomy': 'autonomía media',
 'avg_trust': 'confianza media',
 'truth_error': 'error de verdad',
 'democratic_quality': 'calidad democrática',
 'water_stock': 'reserva de agua',
 'food_stock': 'reserva de alimento',
 'energy_stock': 'reserva de energía',
 'shelter_capacity': 'capacidad de vivienda',
 'health_capacity': 'capacidad de salud',
 'care_capacity': 'capacidad de cuidados',
 'education_capacity': 'capacidad educativa',
 'mobility_capacity': 'capacidad de movilidad',
 'manufacturing_capacity': 'capacidad de fabricación',
 'storage_capacity': 'capacidad de almacenamiento',
 'governance_capacity': 'capacidad de gobernanza',
 'knowledge_capacity': 'capacidad de conocimiento',
 'resilience_capacity': 'capacidad de resiliencia',
 'repair_materials': 'materiales de reparación',
 'waste': 'residuo',
 'soil_health': 'salud del suelo',
 'biodiversity': 'biodiversidad',
 'watershed': 'cuenca hídrica',
 'local_pollution': 'contaminación local',
 'renewable_infrastructure': 'infraestructura renovable',
 'top_priority_domain': 'dominio de mayor prioridad',
 'top_priority': 'mayor prioridad',
 'top_labor_domain': 'dominio de mayor trabajo',
 'top_labor_share': 'cuota mayor de trabajo',
 'priority': 'prioridad',
 'explanation': 'explicación',
 'need': 'necesidad',
 'available': 'disponible',
 'gap': 'brecha',
 'satisfaction': 'satisfacción',
 'labor_share': 'cuota de trabajo',
 'contribution_time': 'tiempo de contribución',
 'stock_or_capacity': 'reserva o capacidad',
 'boundary_penalty': 'penalización de límite',
 'activated_flows': 'flujos activados',
 'wellbeing': 'bienestar',
 'unmet_basic': 'necesidades básicas no cubiertas',
 'overshoot': 'exceso planetario',
 'mean_boundary_pressure': 'presión media de límites',
 'worst_boundary': 'peor límite',
 'worst_boundary_pressure': 'presión del peor límite',
 'waste_stock': 'reserva de residuos',
 'global_transfers': 'transferencias globales',
 'contribution_time_per_person': 'tiempo de contribución por persona',
 'satisfaction_inequality': 'desigualdad de satisfacción',
 'resilience_index': 'índice de resiliencia',
 'circularity_index': 'índice de circularidad',
 'coordination_quality': 'calidad de coordinación',
 'basic_buffer_months': 'meses de colchón básico',
 'macro_capacity': 'capacidad macro',
 'planetary_reproduction_index': 'índice de reproducción planetaria',
 'dimension': 'dimensión',
 'name': 'nombre',
 'short': 'abreviatura',
 'question': 'pregunta',
 'contract_role': 'papel contractual',
 'economic_replacement': 'sustitución económica',
 'weight': 'peso',
 'effects': 'efectos',
 'potencies': 'potencias',
 'substance': 'sustancia',
 'matter': 'materia',
 'causality': 'causalidad',
 'time': 'tiempo',
 'intensity': 'intensidad',
 'existence': 'existencia',
 'difference': 'diferencia',
 'determination': 'determinación',
 'phenomena': 'fenómenos',
 'angle_direction': 'dirección angular'}
LOCAL_BIOME_NAMES = {'equatorial_forest': 'bosque ecuatorial',
 'temperate_mixed': 'zona templada mixta',
 'drylands': 'tierras áridas',
 'coastal_delta': 'delta costero',
 'mountain_water': 'zona acuífera de montaña',
 'urban_corridor': 'corredor urbano',
 'steppe_grainland': 'estepa cerealista',
 'subpolar_periphery': 'periferia subpolar'}
LOCAL_NOTE_TEXTS = {'contribution time directed by truth-vector priority, not wage/price': 'el tiempo de contribución se dirige por prioridad del vector de verdad, no por '
                                                                        'salario ni precio',
 'surplus and deficit matched by urgencia, not purchasing power': 'excedente y déficit se emparejan por urgencia, no por poder adquisitivo',
 'need satisfaction accepted through existence/intensity/time, not purchasing power': 'la satisfacción de necesidad se acepta por existencia, intensidad y '
                                                                                      'tiempo, no por poder adquisitivo',
 'housing access through real need and capacity, not rent/price': 'el acceso a vivienda sigue necesidad y capacidad reales, no renta ni precio',
 'service is used as social effect, not purchased service value': 'el servicio se usa como efecto social, no como valor de servicio comprado'}
LOCAL_DIRECTION_TERMS = {'angle': 'dirección', 'difference': 'diferencia', 'determination': 'determinación', 'validity': 'validez'}
LOCAL_SUMMARY_KEYS = {'model': 'modelo',
 'scenario': 'escenario',
 'seed': 'semilla',
 'steps': 'pasos',
 'regions': 'regiones',
 'communes': 'comunas',
 'initial': 'inicial',
 'final': 'final',
 'delta': 'cambio',
 'boundary_pressures': 'presiones de límites',
 'planner': 'planificador'}
COMMUNE_SUFFIX = 'Comuna'
UNMAPPED_LABEL = 'sin asignar'
NONE_LABEL = 'ninguno'

LOCAL_FIELD_LABELS.update({'avg_truth_error': 'error medio de verdad', 'boundary_penalty': 'penalización de límite'})
DISPLAY_LEGACY_LABELS.update({'buy/sell/import/export': 'compra, venta, importación y exportación', 'buy/rent': 'compra o renta', 'buy/service_purchase': 'compra de servicio'})
DISPLAY_ACTION_LABELS.update({'causal_transfer_to_need': 'transferencia causal hacia necesidad', 'stabilize_shelter_existence': 'estabilizar existencia de vivienda', 'accept_service_effect': 'aceptar efecto de servicio'})
LOCAL_EXPLANATION_FORMAT = 'brecha de necesidad=%.3f potencias=%.3f confianza=%.3f penalización de límite=%.3f'

FORCED_TERMINAL_WIDTH = 0

def display_domain(domain: str) -> str:
    return DISPLAY_DOMAIN_NAMES.get(domain, domain)

def display_sector(sector: str) -> str:
    return DISPLAY_SECTOR_NAMES.get(sector, sector)

def display_boundary(boundary: str) -> str:
    return DISPLAY_BOUNDARY_NAMES.get(boundary, boundary)

def display_scenario(scenario: str) -> str:
    return SCENARIO_INTERNAL_TO_LABEL.get(scenario, scenario)

def display_kind(kind: str) -> str:
    return DISPLAY_KIND_LABELS.get(kind, kind)

def display_legacy(term: str) -> str:
    return DISPLAY_LEGACY_LABELS.get(term, term)

def display_action(action: str) -> str:
    return DISPLAY_ACTION_LABELS.get(action, action)

def localized_file(key: str) -> str:
    return OUTPUT_FILE_NAMES.get(key, key)

def localized_label(key: str, fallback: str = "") -> str:
    return UI_LABELS.get(key, LOCAL_FIELD_LABELS.get(key, fallback or key))

def localized_text(key: str, fallback: str = "") -> str:
    return UI_TEXT.get(key, fallback or key)


def display_biome(biome: str) -> str:
    return LOCAL_BIOME_NAMES.get(biome, biome)


def local_field(key: str) -> str:
    return LOCAL_FIELD_LABELS.get(key, localized_label(key, key))


def local_note(note: str) -> str:
    return LOCAL_NOTE_TEXTS.get(note, note)


def local_summary_key(key: str) -> str:
    return LOCAL_SUMMARY_KEYS.get(key, local_field(key))


def localize_cell(key: str, value: object) -> object:
    if key in ("domain", "top_priority_domain", "top_labor_domain"):
        return display_domain(str(value)) if value not in ("none", "") else NONE_LABEL
    if key == "sector":
        return display_sector(str(value)) if value else value
    if key == "biome":
        return display_biome(str(value))
    if key == "worst_boundary":
        return display_boundary(str(value))
    if key == "kind":
        return display_kind(str(value))
    if key == "legacy_term_replaced":
        return display_legacy(str(value))
    if key == "action":
        return display_action(str(value))
    if key == "contract_validity":
        return str(value)
    if key == "note":
        return local_note(str(value))
    return value


def localize_row(row: Dict[str, object]) -> Dict[str, object]:
    return {local_field(k): localize_cell(k, v) for k, v in row.items()}


def localize_metric_row(row: Dict[str, object]) -> Dict[str, object]:
    return {local_field(k): localize_cell(k, v) for k, v in row.items()}


def write_dict_rows_localized(path: str, rows: List[Dict[str, object]], field_order: Optional[List[str]] = None) -> None:
    if not rows:
        return
    if field_order is None:
        field_order = list(rows[0].keys())
    localized_fields = [local_field(f) for f in field_order]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=localized_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({local_field(k): localize_cell(k, row.get(k, "")) for k in field_order})

def set_forced_terminal_width(width: int) -> None:
    global FORCED_TERMINAL_WIDTH
    try:
        FORCED_TERMINAL_WIDTH = int(width)
    except Exception:
        FORCED_TERMINAL_WIDTH = 0
    if FORCED_TERMINAL_WIDTH < 1:
        FORCED_TERMINAL_WIDTH = 0


# ---------------------------------------------------------------------------
# Utility functions

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if abs(b) < 1e-12:
        return default
    return a / b


def scale4(x: float) -> float:
    """Convert a 0..1 normalized number to the 0..4 truth scale."""
    return 4.0 * clamp(x)


def mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = list(values)
    if not vals:
        return default
    return sum(vals) / float(len(vals))


def weighted_mean(items: Iterable[Tuple[float, float]], default: float = 0.0) -> float:
    total_w = 0.0
    total = 0.0
    for value, weight in items:
        total += value * weight
        total_w += weight
    if total_w <= 1e-12:
        return default
    return total / total_w


def weighted_gini(items: Iterable[Tuple[float, float]]) -> float:
    """Weighted Gini for inequality of satisfaction/wellbeing.

    0 means equal distribution. 1 would mean maximum inequality.
    This is distributional diagnostics, not moral value in money terms.
    """
    data = [(max(0.0, v), max(0.0, w)) for v, w in items if w > 0.0]
    if not data:
        return 0.0
    data.sort(key=lambda x: x[0])
    total_w = sum(w for _, w in data)
    total_xw = sum(v * w for v, w in data)
    if total_w <= 1e-12 or total_xw <= 1e-12:
        return 0.0
    cum_w = 0.0
    cum_xw = 0.0
    area = 0.0
    prev_w_share = 0.0
    prev_x_share = 0.0
    for value, weight in data:
        cum_w += weight
        cum_xw += value * weight
        w_share = cum_w / total_w
        x_share = cum_xw / total_xw
        area += (x_share + prev_x_share) * (w_share - prev_w_share) / 2.0
        prev_w_share = w_share
        prev_x_share = x_share
    return clamp(1.0 - 2.0 * area)


def normalized_need_gap(need: float, available: float) -> float:
    """0 means covered, 1 means almost completely missing."""
    if need <= 1e-12:
        return 0.0
    return clamp((need - available) / need)


def sat_ratio(available: float, need: float) -> float:
    if need <= 1e-12:
        return 1.0
    return clamp(available / need)


def lognormal_near(rng: random.Random, center: float, spread: float) -> float:
    """Small helper to avoid relying on statistics/numpy."""
    return center * math.exp(rng.gauss(0.0, spread))


def format_big(x: float) -> str:
    abs_x = abs(x)
    if abs_x >= 1_000_000_000:
        return "%.3f %s" % (x / 1_000_000_000.0, UNIT_LABELS.get("billion", "billion"))
    if abs_x >= 1_000_000:
        return "%.3f %s" % (x / 1_000_000.0, UNIT_LABELS.get("million", "million"))
    if abs_x >= 1_000:
        return "%.3f %s" % (x / 1_000.0, UNIT_LABELS.get("thousand", "thousand"))
    return "%.3f" % x



def truth_digit(value: float) -> int:
    """Convert a 0..4 truth value to a stacked digit 0..4."""
    return int(round(clamp(value, 0.0, 4.0)))


def truth_stack_score_0_4(values: Dict[str, float]) -> float:
    """Weighted stacked truth score on 0..4 scale. Not price, not value."""
    total = 0.0
    weight_sum = 0.0
    for dim in TRUTH_DIMS:
        weight = TRUTH_WEIGHTS.get(dim, 0.0)
        total += clamp(values.get(dim, 0.0), 0.0, 4.0) * weight
        weight_sum += weight
    if weight_sum <= 0.0:
        return 0.0
    return total / weight_sum


def truth_stack_base5(values: Dict[str, float]) -> str:
    """Stack the 12 dimensions into a base-5 code in TRUTH_DIMS order.

    Example: 343233223433 means:
    causality=3, time=4, intensity=3, ... angle_direction=3.
    This is a number-like truth signature, not money.
    """
    return "".join(str(truth_digit(values.get(dim, 0.0))) for dim in TRUTH_DIMS)


def truth_stack_decimal(values: Dict[str, float]) -> int:
    code = truth_stack_base5(values)
    try:
        return int(code, 5)
    except ValueError:
        return 0


def compact_truth_stack(values: Dict[str, float]) -> str:
    parts = []
    for dim in TRUTH_DIMS:
        guide = DIMENSION_GUIDE.get(dim, {})
        short = guide.get("short", dim[:2])
        parts.append("%s=%.2f" % (short, clamp(values.get(dim, 0.0), 0.0, 4.0)))
    return " | ".join(parts)


def dimension_meaning_summary(values: Dict[str, float]) -> str:
    if not values:
        return 'no hay valores de verdad'
    sorted_dims = sorted(TRUTH_DIMS, key=lambda d: values.get(d, 0.0), reverse=True)
    strongest = sorted_dims[:3]
    weakest = sorted_dims[-3:]
    strong_txt = ", ".join("%s %.2f" % (DIMENSION_GUIDE[d]["name"], values.get(d, 0.0)) for d in strongest)
    weak_txt = ", ".join("%s %.2f" % (DIMENSION_GUIDE[d]["name"], values.get(d, 0.0)) for d in weakest)
    return "%s: %s; %s: %s" % ('fuerte', strong_txt, 'débil o por comprobar', weak_txt)


def contract_conditions_for_flow(kind: str, domain: str, values: Dict[str, float]) -> Tuple[str, str]:
    if not values:
        return "experimental", 'faltan valores de verdad; solo se permite un ensayo observador.'
    conditions: List[str] = []
    causality = values.get("causality", 0.0)
    time_v = values.get("time", 0.0)
    intensity = values.get("intensity", 0.0)
    existence = values.get("existence", 0.0)
    potencies = values.get("potencies", 0.0)
    effects = values.get("effects", 0.0)
    substance = values.get("substance", 0.0)
    matter = values.get("matter", 0.0)
    difference = values.get("difference", 0.0)
    determination = values.get("determination", 0.0)
    phenomena = values.get("phenomena", 0.0)
    angle = values.get("angle_direction", 0.0)
    def n(dim: str) -> str:
        return DIMENSION_GUIDE[dim]["name"]
    if causality < 1.6:
        conditions.append("%s %s" % (n("causality"), 'baja: primero exigir investigación causal, ensayo piloto o diagnóstico local.'))
    elif causality >= 3.0:
        conditions.append("%s %s" % (n("causality"), 'alta: la cadena de efecto es plausible y puede priorizarse.'))
    else:
        conditions.append("%s %s" % (n("causality"), 'media: el contrato contiene auditoría y deber de corrección.'))
    if time_v >= 3.0:
        conditions.append("%s %s" % (n("time"), 'alto: vía urgente o rápida, plazo corto, revisión posterior.'))
    elif time_v < 1.5:
        conditions.append("%s %s" % (n("time"), 'bajo: planificable, sin desplazar otros campos por urgencia.'))
    if intensity >= 3.0:
        conditions.append("%s %s" % (n("intensity"), 'alta: la fuerza de despliegue puede subir más allá de la cuota normal.'))
    if existence < 1.5:
        conditions.append("%s %s" % (n("existence"), 'incierta: solicitar informes de personas afectadas y medición.'))
    if potencies < 1.8:
        conditions.append("%s %s" % (n("potencies"), 'escasas: primero construir capacidades, herramientas o capacidad grupal.'))
    if effects >= 3.0:
        conditions.append("%s %s" % (n("effects"), 'altos: la consecuencia sistémica positiva se reconoce como beneficio social.'))
    if substance < 1.8:
        conditions.append("%s %s" % (n("substance"), 'escasa: limitar liberación material y asegurar fuente circular o sustituta.'))
    if matter < 1.8:
        conditions.append("%s %s" % (n("matter"), 'desfavorable: aclarar logística, cercanía o infraestructura local.'))
    if difference >= 3.0:
        conditions.append("%s %s" % (n("difference"), 'alta: la brecha real entre necesidad y estado legitima la acción.'))
    elif difference < 1.2 and kind != "contribution_offer":
        conditions.append("%s %s" % (n("difference"), 'baja: sin trato prioritario; solo mantenimiento o prevención.'))
    if determination < 1.8:
        conditions.append("%s %s" % (n("determination"), 'débil: se requiere retroalimentación democrática y derecho de objeción.'))
    if phenomena < 1.6:
        conditions.append("%s %s" % (n("phenomena"), 'débiles: mejorar visibilidad, informes y auditoría.'))
    if angle < 1.5:
        conditions.append("%s %s" % (n("angle_direction"), 'negativa: rediseñar la acción y evitar daño ecológico o social.'))
    elif angle >= 3.0:
        conditions.append("%s %s" % (n("angle_direction"), 'regenerativa: la acción encaja con la dirección planetaria.'))
    else:
        conditions.append("%s %s" % (n("angle_direction"), 'condicional: limitar efectos secundarios y efecto climático.'))
    cat = TRADE_CATALOG.get(domain, {})
    if cat.get("ecology"):
        conditions.append("%s: %s" % ('cláusula ecológica', cat["ecology"]))
    if cat.get("climate"):
        conditions.append("%s: %s" % ('cláusula climática', cat["climate"]))
    if angle < 1.2 or (causality < 1.2 and effects < 2.0):
        validity = "blocked"
    elif causality < 1.8 or existence < 1.5 or determination < 1.5:
        validity = "experimental"
    elif substance < 1.6 or matter < 1.6 or angle < 2.1 or potencies < 1.6:
        validity = "conditional"
    else:
        validity = "valid"
    return validity, " ".join(conditions)


def catalog_value(domain: str, key: str) -> str:
    return TRADE_CATALOG.get(domain, {}).get(key, "")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class TruthVector:
    """Stacked logical truth values on a 0..4 scale."""

    domain: str
    values: Dict[str, float]
    commune: str = ""
    region: str = ""
    explanation: str = ""

    def priority(self) -> float:
        """Priority is not price. It is weighted urgencia/effect/difference."""
        total = 0.0
        weight_sum = 0.0
        for dim in TRUTH_DIMS:
            weight = TRUTH_WEIGHTS.get(dim, 0.0)
            total += clamp(self.values.get(dim, 0.0), 0.0, 4.0) * weight
            weight_sum += weight
        if weight_sum <= 0.0:
            return 0.0
        return total / (4.0 * weight_sum)

    def as_row(self, step: int) -> Dict[str, object]:
        row = {
            "step": step,
            "region": self.region,
            "commune": self.commune,
            "domain": self.domain,
            "priority": round(self.priority(), 6),
            "explanation": self.explanation,
        }
        for dim in TRUTH_DIMS:
            row[dim] = round(self.values.get(dim, 0.0), 6)
        return row


@dataclass
class EffectFlow:
    """A non-market action record.

    It replaces buy/sell/import/export with causal effect activation:
    - need_acceptance: what older language would call buying/consuming
    - contribution_offer: what older language would call selling/labour supply
    - planetary_transfer: what older language would call trade/import/export

    The numeric field is called activated_effect, not price, worth or value.
    """

    step: int
    kind: str
    legacy_term_replaced: str
    action: str
    domain: str
    sector: str
    from_region: str
    from_commune: str
    to_region: str
    to_commune: str
    activated_effect: float
    causal_link: str
    direction_vector: str
    values: Dict[str, float]
    note: str = ""
    trade_object: str = ""
    meant_as: str = ""
    product_examples: str = ""
    workplace_examples: str = ""
    service_examples: str = ""
    ecological_clause: str = ""
    climate_clause: str = ""
    contract_validity: str = ""
    contract_conditions: str = ""
    truth_stack_score_0_4: float = 0.0
    truth_stack_priority_0_1: float = 0.0
    truth_stack_base5: str = ""
    truth_stack_decimal: int = 0
    truth_stack_compact: str = ""
    dimension_meaning: str = ""

    def as_row(self) -> Dict[str, object]:
        row = {
            "step": self.step,
            "kind": self.kind,
            "legacy_term_replaced": self.legacy_term_replaced,
            "action": self.action,
            "domain": self.domain,
            "sector": self.sector,
            "trade_object": self.trade_object,
            "meant_as": self.meant_as,
            "product_examples": self.product_examples,
            "workplace_examples": self.workplace_examples,
            "service_examples": self.service_examples,
            "ecological_clause": self.ecological_clause,
            "climate_clause": self.climate_clause,
            "contract_validity": self.contract_validity,
            "contract_conditions": self.contract_conditions,
            "truth_stack_score_0_4": round(self.truth_stack_score_0_4, 6),
            "truth_stack_priority_0_1": round(self.truth_stack_priority_0_1, 6),
            "truth_stack_base5": self.truth_stack_base5,
            "truth_stack_decimal": self.truth_stack_decimal,
            "truth_stack_compact": self.truth_stack_compact,
            "dimension_meaning": self.dimension_meaning,
            "from_region": self.from_region,
            "from_commune": self.from_commune,
            "to_region": self.to_region,
            "to_commune": self.to_commune,
            "activated_effect": round(self.activated_effect, 6),
            "causal_link": self.causal_link,
            "direction_vector": self.direction_vector,
            "note": self.note,
        }
        for dim in TRUTH_DIMS:
            row[dim] = round(self.values.get(dim, 0.0), 6)
        return row


@dataclass
class MacroAccountRow:
    """fila de cuenta macroplanetaria sin categorías de valor monetario."""

    step: int
    domain: str
    sector: str
    need: float
    available: float
    gap: float
    satisfaction: float
    priority: float
    labor_share: float
    contribution_time: float
    stock_or_capacity: float
    boundary_penalty: float
    truth_error: float
    democratic_quality: float
    activated_flows: int

    def as_row(self) -> Dict[str, object]:
        return {
            "step": self.step,
            "domain": self.domain,
            "sector": self.sector,
            "need": round(self.need, 6),
            "available": round(self.available, 6),
            "gap": round(self.gap, 6),
            "satisfaction": round(self.satisfaction, 6),
            "priority": round(self.priority, 6),
            "labor_share": round(self.labor_share, 6),
            "contribution_time": round(self.contribution_time, 6),
            "stock_or_capacity": round(self.stock_or_capacity, 6),
            "boundary_penalty": round(self.boundary_penalty, 6),
            "truth_error": round(self.truth_error, 6),
            "democratic_quality": round(self.democratic_quality, 6),
            "activated_flows": self.activated_flows,
        }


@dataclass
class BoundaryState:
    """espacio operativo planetario. Los valores son presiones; >1.0 significa exceso."""

    pressures: Dict[str, float]

    def overshoot(self) -> float:
        return sum(max(0.0, self.pressures.get(name, 0.0) - 1.0) for name in BOUNDARY_NAMES)

    def mean_pressure(self) -> float:
        return mean(self.pressures.get(name, 0.0) for name in BOUNDARY_NAMES)

    def worst(self) -> Tuple[str, float]:
        if not self.pressures:
            return "none", 0.0
        return max(self.pressures.items(), key=lambda kv: kv[1])

    def penalty(self) -> float:
        """Overshoot reduces system effectiveness but never makes action impossible."""
        overs = self.overshoot()
        # Smooth penalty. At zero overshoot = 1.0, at severe overshoot maybe ~0.55.
        return clamp(1.0 / (1.0 + 0.33 * overs), 0.45, 1.0)

    def apply_impacts(self, impacts: Dict[str, float], regeneration: Dict[str, float]) -> None:
        # Scale constants keep values stable for synthetic runs.
        for name in BOUNDARY_NAMES:
            before = self.pressures.get(name, 0.7)
            pressure = before
            pressure += impacts.get(name, 0.0)
            pressure -= regeneration.get(name, 0.0)
            # Natural repair is slow if under low pressure; degradation is sticky above 1.
            if pressure < 0.75:
                pressure += 0.005 * (0.75 - pressure)
            if pressure > 1.0:
                pressure += 0.002 * (pressure - 1.0)
            self.pressures[name] = clamp(pressure, 0.2, 2.2)


@dataclass
class PopulationCohort:
    name: str
    size: float
    health: float
    education: float
    autonomy: float
    trust: float
    skill: Dict[str, float]
    age_factor: float = 1.0

    def productive_time(self) -> float:
        # Labour is not bought/sold. This is available contribution time.
        return self.size * self.age_factor * clamp(0.35 + 0.65 * self.health) * clamp(0.45 + 0.55 * self.autonomy)

    def update_from_satisfaction(self, satisfaction: Dict[str, float], governance_quality: float, privacy_pressure: float) -> None:
        basic = 0.40 * satisfaction.get("water", 1.0) + 0.35 * satisfaction.get("food", 1.0) + 0.25 * satisfaction.get("shelter", 1.0)
        service = 0.45 * satisfaction.get("health", 1.0) + 0.25 * satisfaction.get("care", 1.0) + 0.20 * satisfaction.get("education", 1.0) + 0.10 * satisfaction.get("mobility", 1.0)
        civic = 0.34 * satisfaction.get("governance", 1.0) + 0.33 * satisfaction.get("knowledge", 1.0) + 0.33 * satisfaction.get("resilience", 1.0)
        energy = satisfaction.get("energy", 1.0)
        # Health moves slowly; severe basic deficits hit it fast.
        health_delta = 0.018 * (basic - 0.78) + 0.010 * (service - 0.75) + 0.006 * (energy - 0.70)
        self.health = clamp(self.health + health_delta, 0.05, 1.0)
        # Education responds to education satisfaction, not instantly.
        self.education = clamp(self.education + 0.006 * (satisfaction.get("education", 1.0) - 0.55) + 0.003 * (satisfaction.get("knowledge", 1.0) - 0.55), 0.05, 1.0)
        # Autonomy drops under unmet basics and high privacy/control pressure; it rises with civic capability.
        self.autonomy = clamp(self.autonomy + 0.010 * (mean(satisfaction.values(), 0.9) - 0.72) + 0.006 * (civic - 0.65) - 0.018 * privacy_pressure, 0.05, 1.0)
        # Trust is a local truth-feedback quality. It falls when the system claims truth but fails people.
        self.trust = clamp(self.trust + 0.018 * (mean(satisfaction.values(), 0.9) - 0.70) + 0.016 * (governance_quality - 0.5) + 0.008 * (civic - 0.65) - 0.012 * privacy_pressure, 0.02, 1.0)
        # Skills improve with education and degrade slowly if health is bad.
        for k in list(self.skill.keys()):
            self.skill[k] = clamp(self.skill[k] + 0.003 * (self.education - 0.5) + 0.002 * (self.health - 0.5), 0.05, 1.0)


@dataclass
class Commune:
    name: str
    region_name: str
    biome: str
    cohorts: List[PopulationCohort]
    stocks: Dict[str, float]
    capacities: Dict[str, float]
    environment: Dict[str, float]
    group_base: Dict[str, float]
    democratic_quality: float
    truth_error: float = 0.15
    last_satisfaction: Dict[str, float] = field(default_factory=dict)
    last_priorities: Dict[str, float] = field(default_factory=dict)
    last_labor_shares: Dict[str, float] = field(default_factory=dict)
    last_truth_values: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def population(self) -> float:
        return sum(c.size for c in self.cohorts)

    def productive_time(self) -> float:
        return sum(c.productive_time() for c in self.cohorts)

    def average_health(self) -> float:
        return weighted_mean(((c.health, c.size) for c in self.cohorts), default=0.7)

    def average_education(self) -> float:
        return weighted_mean(((c.education, c.size) for c in self.cohorts), default=0.6)

    def average_autonomy(self) -> float:
        return weighted_mean(((c.autonomy, c.size) for c in self.cohorts), default=0.7)

    def average_trust(self) -> float:
        return weighted_mean(((c.trust, c.size) for c in self.cohorts), default=0.6)

    def skill(self, field_name: str) -> float:
        return weighted_mean(((c.skill.get(field_name, 0.4), c.size) for c in self.cohorts), default=0.4)

    def need(self, domain: str) -> float:
        pop = self.population()
        if domain == "health":
            # More need if health is low.
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.75 * (1.0 - self.average_health()))
        if domain == "care":
            child_elder_share = 0.0
            for c in self.cohorts:
                if c.name in ("children", "elders"):
                    child_elder_share += c.size
            dependency = safe_div(child_elder_share, pop, 0.33)
            return pop * NEED_PER_PERSON[domain] * (0.65 + 1.35 * dependency)
        if domain == "education":
            # Higher education demand if education is low; still lifelong education if high.
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.75 * (1.0 - self.average_education()))
        if domain == "mobility":
            return pop * NEED_PER_PERSON[domain] * (0.8 + 0.3 * self.environment.get("remoteness", 0.5))
        if domain == "governance":
            # Coordination need rises with complexity, low trust and truth error.
            complexity = 0.45 + 0.35 * self.environment.get("remoteness", 0.5) + 0.20 * self.truth_error
            legitimacy_gap = 1.0 - 0.5 * self.democratic_quality - 0.5 * self.average_trust()
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.55 * complexity + 0.60 * max(0.0, legitimacy_gap))
        if domain == "knowledge":
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.65 * (1.0 - self.average_education()) + 0.25 * (1.0 - self.environment.get("renewable_infrastructure", 0.5)))
        if domain == "manufacturing":
            repair_gap = normalized_need_gap(max(1.0, pop * 0.18), self.stocks.get("repair_materials", 0.0))
            capacity_gap = normalized_need_gap(max(1.0, pop * NEED_PER_PERSON[domain]), self.capacities.get("manufacturing", 0.0))
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.65 * repair_gap + 0.40 * capacity_gap)
        if domain == "storage":
            basic_need = self.need("water") + self.need("food") + self.need("energy")
            basic_stock = self.stocks.get("water", 0.0) + self.stocks.get("food", 0.0) + self.stocks.get("energy", 0.0)
            buffer_gap = normalized_need_gap(1.20 * basic_need, basic_stock)
            return pop * NEED_PER_PERSON[domain] * (0.70 + 1.10 * buffer_gap)
        if domain == "resilience":
            climate_exposure = self.environment.get("local_pollution", 0.2) + (1.0 - self.environment.get("watershed", 0.7))
            buffer_gap = normalized_need_gap(max(1.0, pop * 0.60), self.stocks.get("water", 0.0) + self.stocks.get("food", 0.0))
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.45 * climate_exposure + 0.55 * buffer_gap)
        if domain in NEED_PER_PERSON:
            return pop * NEED_PER_PERSON[domain]
        return 0.0

    def available_for_need(self, domain: str) -> float:
        if domain in CONSUMABLE_DOMAINS:
            return self.stocks.get(domain, 0.0)
        if domain in SERVICE_DOMAINS:
            return self.capacities.get(domain, 0.0)
        if domain in CAPACITY_DOMAINS:
            return self.capacities.get(domain, 0.0)
        if domain == "repair":
            return self.stocks.get("repair_materials", 0.0)
        if domain == "ecology":
            # Deficit relative to healthy ecosystems.
            pop = self.population()
            soil_gap = max(0.0, 1.0 - self.environment.get("soil_health", 0.7))
            bio_gap = max(0.0, 1.0 - self.environment.get("biodiversity", 0.7))
            water_gap = max(0.0, 1.0 - self.environment.get("watershed", 0.7))
            return pop * (1.0 - mean([soil_gap, bio_gap, water_gap]))
        if domain == "waste":
            return self.stocks.get("waste", 0.0)
        return 0.0

    def ecology_need(self) -> float:
        pop = self.population()
        soil_gap = max(0.0, 1.0 - self.environment.get("soil_health", 0.7))
        bio_gap = max(0.0, 1.0 - self.environment.get("biodiversity", 0.7))
        water_gap = max(0.0, 1.0 - self.environment.get("watershed", 0.7))
        pollution = self.environment.get("local_pollution", 0.25)
        return pop * (0.18 + 0.50 * mean([soil_gap, bio_gap, water_gap, pollution]))

    def waste_need(self) -> float:
        # Waste is an unresolved material difference. High stock => high need.
        return max(1.0, self.population() * 0.10)

    def truth_vector(self, domain: str, global_boundary: BoundaryState, planner: "EffectPlanner") -> TruthVector:
        pop = self.population()
        env_penalty = 1.0 - global_boundary.penalty()
        if domain == "ecology":
            need = self.ecology_need()
            # Ecology availability is environmental integrity.
            available = max(0.0, pop * mean([
                self.environment.get("soil_health", 0.7),
                self.environment.get("biodiversity", 0.7),
                self.environment.get("watershed", 0.7),
                1.0 - self.environment.get("local_pollution", 0.2),
            ]))
            gap = clamp(need / max(pop * 0.70, 1.0))
        elif domain == "waste":
            need = self.waste_need()
            available = max(0.0, need - self.stocks.get("waste", 0.0))
            gap = clamp(self.stocks.get("waste", 0.0) / max(need, 1.0))
        else:
            need = self.need(domain)
            available = self.available_for_need(domain)
            gap = normalized_need_gap(need, available)

        domain_skill = self.skill(planner.skill_for_domain(domain))
        group_strength = self.group_base.get(planner.group_for_domain(domain), 0.4)
        local_potencies = clamp(0.45 * domain_skill + 0.35 * group_strength + 0.20 * self.democratic_quality)
        substance = clamp(0.35 * sat_ratio(self.stocks.get("repair_materials", 0.0), max(1.0, pop * 0.05)) +
                          0.25 * sat_ratio(self.stocks.get("energy", 0.0), max(1.0, self.need("energy") * 0.35)) +
                          0.20 * self.environment.get("watershed", 0.7) +
                          0.20 * self.environment.get("soil_health", 0.7))
        matter = clamp(0.55 * (1.0 - self.environment.get("remoteness", 0.5)) + 0.45 * sat_ratio(self.capacities.get("mobility", 0.0), max(1.0, self.need("mobility"))))
        criticality = planner.domain_criticality.get(domain, 0.5)
        time_urgencia = clamp(0.45 * gap + 0.40 * criticality + 0.15 * env_penalty)
        intensity = clamp(0.70 * gap + 0.20 * criticality + 0.10 * (1.0 - self.average_health()))
        # Democracy should influence determination, but not allow a majority to erase critical needs.
        collective_claim = clamp(0.55 * gap + 0.25 * self.democratic_quality + 0.20 * self.average_trust())
        # Phenomena combines measured and reported reality; truth_error is noise/uncertainty.
        phenomena = clamp(gap * (1.0 - 0.50 * self.truth_error) + self.average_trust() * 0.15 + self.democratic_quality * 0.10)
        angle = planner.angle_alignment(domain, global_boundary, self)
        values = {
            "causality": scale4(planner.causal_confidence.get(domain, 0.65)),
            "time": scale4(time_urgencia),
            "intensity": scale4(intensity),
            "existence": scale4(clamp(0.7 * gap + 0.3 * criticality)),
            "potencies": scale4(local_potencies),
            "effects": scale4(planner.effect_weight.get(domain, 0.6)),
            "substance": scale4(substance),
            "matter": scale4(matter),
            "difference": scale4(gap),
            "determination": scale4(collective_claim),
            "phenomena": scale4(phenomena),
            "angle_direction": scale4(angle),
        }
        return TruthVector(
            domain=domain,
            values=values,
            commune=self.name,
            region=self.region_name,
            explanation=LOCAL_EXPLANATION_FORMAT % (
                gap, local_potencies, self.average_trust(), global_boundary.penalty()
            ),
        )

    def update_truth_error(self, avg_satisfaction: float, planner: "EffectPlanner") -> None:
        # More democratic feedback and trust reduces truth error. High centralization raises it.
        correction = 0.018 * self.democratic_quality * self.average_trust() * planner.democratic_feedback
        failure = 0.014 * max(0.0, 0.68 - avg_satisfaction)
        central_error = 0.010 * planner.centralization * (1.0 - self.democratic_quality)
        self.truth_error = clamp(self.truth_error - correction + failure + central_error, 0.02, 0.75)


@dataclass
class Region:
    name: str
    biome: str
    communes: List[Commune]
    logistic_hub: float
    climate_risk: float

    def population(self) -> float:
        return sum(c.population() for c in self.communes)


@dataclass
class GlobalMetrics:
    step: int
    population: float
    wellbeing: float
    unmet_basic: float
    avg_trust: float
    avg_autonomy: float
    avg_health: float
    avg_education: float
    avg_truth_error: float
    overshoot: float
    mean_boundary_pressure: float
    worst_boundary: str
    worst_boundary_pressure: float
    waste_stock: float
    repair_materials: float
    food_stock: float
    water_stock: float
    energy_stock: float
    global_transfers: float
    contribution_time: float
    contribution_time_per_person: float
    satisfaction_inequality: float
    resilience_index: float
    circularity_index: float
    coordination_quality: float
    basic_buffer_months: float
    macro_capacity: float
    planetary_reproduction_index: float

    def as_row(self) -> Dict[str, object]:
        return {
            "step": self.step,
            "population": round(self.population, 3),
            "wellbeing": round(self.wellbeing, 6),
            "unmet_basic": round(self.unmet_basic, 6),
            "avg_trust": round(self.avg_trust, 6),
            "avg_autonomy": round(self.avg_autonomy, 6),
            "avg_health": round(self.avg_health, 6),
            "avg_education": round(self.avg_education, 6),
            "avg_truth_error": round(self.avg_truth_error, 6),
            "overshoot": round(self.overshoot, 6),
            "mean_boundary_pressure": round(self.mean_boundary_pressure, 6),
            "worst_boundary": self.worst_boundary,
            "worst_boundary_pressure": round(self.worst_boundary_pressure, 6),
            "waste_stock": round(self.waste_stock, 3),
            "repair_materials": round(self.repair_materials, 3),
            "food_stock": round(self.food_stock, 3),
            "water_stock": round(self.water_stock, 3),
            "energy_stock": round(self.energy_stock, 3),
            "global_transfers": round(self.global_transfers, 3),
            "contribution_time": round(self.contribution_time, 3),
            "contribution_time_per_person": round(self.contribution_time_per_person, 6),
            "satisfaction_inequality": round(self.satisfaction_inequality, 6),
            "resilience_index": round(self.resilience_index, 6),
            "circularity_index": round(self.circularity_index, 6),
            "coordination_quality": round(self.coordination_quality, 6),
            "basic_buffer_months": round(self.basic_buffer_months, 6),
            "macro_capacity": round(self.macro_capacity, 3),
            "planetary_reproduction_index": round(self.planetary_reproduction_index, 6),
        }


# ---------------------------------------------------------------------------
# Planner / policy logic
# ---------------------------------------------------------------------------


@dataclass
class EffectPlanner:
    """Coordinates effects, not prices."""

    democratic_feedback: float = 0.75
    centralization: float = 0.30
    privacy_pressure: float = 0.10
    cooperation: float = 0.82
    sufficiency_norm: float = 0.80
    climate_discipline: float = 0.78
    redistribution_strength: float = 0.85
    innovation_rate: float = 0.40
    logistics_efficiency: float = 0.76
    renewable_bias: float = 0.72

    domain_criticality: Dict[str, float] = field(default_factory=lambda: {
        "water": 1.00,
        "food": 0.95,
        "energy": 0.78,
        "shelter": 0.86,
        "health": 0.90,
        "care": 0.76,
        "education": 0.62,
        "mobility": 0.50,
        "manufacturing": 0.66,
        "storage": 0.64,
        "governance": 0.74,
        "knowledge": 0.68,
        "resilience": 0.82,
        "repair": 0.58,
        "ecology": 0.92,
        "waste": 0.70,
    })

    causal_confidence: Dict[str, float] = field(default_factory=lambda: {
        "water": 0.88,
        "food": 0.82,
        "energy": 0.78,
        "shelter": 0.73,
        "health": 0.76,
        "care": 0.81,
        "education": 0.70,
        "mobility": 0.66,
        "manufacturing": 0.72,
        "storage": 0.77,
        "governance": 0.67,
        "knowledge": 0.69,
        "resilience": 0.63,
        "repair": 0.82,
        "ecology": 0.69,
        "waste": 0.84,
    })

    effect_weight: Dict[str, float] = field(default_factory=lambda: {
        "water": 0.97,
        "food": 0.94,
        "energy": 0.80,
        "shelter": 0.88,
        "health": 0.91,
        "care": 0.80,
        "education": 0.75,
        "mobility": 0.57,
        "manufacturing": 0.74,
        "storage": 0.77,
        "governance": 0.86,
        "knowledge": 0.82,
        "resilience": 0.88,
        "repair": 0.72,
        "ecology": 0.96,
        "waste": 0.76,
    })

    def group_for_domain(self, domain: str) -> str:
        mapping = {
            "water": "water",
            "food": "agriculture",
            "energy": "energy",
            "shelter": "housing",
            "health": "health",
            "care": "care",
            "education": "education",
            "mobility": "logistics",
            "manufacturing": "manufacturing",
            "storage": "storage",
            "governance": "governance",
            "knowledge": "knowledge",
            "resilience": "resilience",
            "repair": "repair",
            "ecology": "ecology",
            "waste": "repair",
        }
        return mapping.get(domain, domain)

    def skill_for_domain(self, domain: str) -> str:
        mapping = {
            "water": "infrastructure",
            "food": "agriculture",
            "energy": "energy",
            "shelter": "construction",
            "health": "health",
            "care": "care",
            "education": "education",
            "mobility": "logistics",
            "manufacturing": "manufacturing",
            "storage": "storage",
            "governance": "governance",
            "knowledge": "knowledge",
            "resilience": "resilience",
            "repair": "repair",
            "ecology": "ecology",
            "waste": "repair",
        }
        return mapping.get(domain, "general")

    def angle_alignment(self, domain: str, boundary: BoundaryState, commune: Commune) -> float:
        # Positive direction means the action solves need while respecting planetary boundaries.
        overs = boundary.overshoot()
        climate = boundary.pressures.get("climate", 0.9)
        pollution = boundary.pressures.get("pollution", 0.8)
        material = boundary.pressures.get("material_throughput", 0.8)
        if domain in ("ecology", "repair", "waste"):
            return clamp(0.82 + 0.16 * min(1.0, overs))
        if domain in ("water", "food", "health", "care"):
            return clamp(0.78 - 0.08 * max(0.0, material - 1.0) + 0.06 * commune.democratic_quality)
        if domain == "energy":
            return clamp(0.55 + 0.35 * self.renewable_bias - 0.20 * max(0.0, climate - 1.0))
        if domain == "mobility":
            return clamp(0.58 + 0.18 * self.logistics_efficiency - 0.16 * max(0.0, climate - 1.0) - 0.08 * max(0.0, pollution - 1.0))
        if domain == "shelter":
            # Repair/reuse shelter is better than new material throughput.
            reuse = sat_ratio(commune.stocks.get("repair_materials", 0.0), max(1.0, commune.population() * 0.10))
            return clamp(0.58 + 0.20 * reuse - 0.12 * max(0.0, material - 1.0))
        if domain == "manufacturing":
            circular = sat_ratio(commune.stocks.get("repair_materials", 0.0), max(1.0, commune.population() * 0.18))
            return clamp(0.50 + 0.25 * circular + 0.18 * self.sufficiency_norm - 0.18 * max(0.0, material - 1.0))
        if domain == "storage":
            return clamp(0.68 + 0.20 * self.sufficiency_norm - 0.06 * max(0.0, material - 1.0))
        if domain in ("governance", "knowledge", "resilience"):
            democratic_direction = 0.50 + 0.35 * commune.democratic_quality + 0.20 * self.democratic_feedback - 0.22 * self.privacy_pressure
            if domain == "resilience":
                democratic_direction += 0.10 * min(1.0, overs)
            return clamp(democratic_direction)
        return clamp(0.65 - 0.08 * max(0.0, overs))

    def labor_shares(self, truth_vectors: List[TruthVector], commune: Commune, boundary: BoundaryState) -> Dict[str, float]:
        # Base shares prevent neglect of long-term fields. Priorities redirect contribution time.
        base = {
            "water": 0.070,
            "food": 0.120,
            "energy": 0.085,
            "shelter": 0.070,
            "health": 0.085,
            "care": 0.075,
            "education": 0.065,
            "mobility": 0.050,
            "manufacturing": 0.060,
            "storage": 0.040,
            "governance": 0.045,
            "knowledge": 0.045,
            "resilience": 0.050,
            "repair": 0.070,
            "ecology": 0.095,
            "waste": 0.070,
        }
        priority = {tv.domain: tv.priority() for tv in truth_vectors}
        # el exceso planetario refuerza ecología, reparación y residuos, y modera los sectores de alto peso material.
        overs = boundary.overshoot()
        for domain in ("ecology", "repair", "waste", "resilience", "storage"):
            priority[domain] = priority.get(domain, 0.0) + 0.16 * min(1.0, overs)
        if boundary.pressures.get("material_throughput", 0.0) > 1.0:
            priority["repair"] = priority.get("repair", 0.0) + 0.08
            priority["manufacturing"] = max(0.0, priority.get("manufacturing", 0.0) - 0.05)
        if boundary.pressures.get("climate", 0.0) > 1.0:
            priority["energy"] = priority.get("energy", 0.0) + 0.10 * self.renewable_bias
            priority["resilience"] = priority.get("resilience", 0.0) + 0.06
            priority["mobility"] = priority.get("mobility", 0.0) - 0.04 * boundary.pressures.get("climate", 1.0)
        # Centralization dampens local truth. Democratic feedback amplifies it.
        local_weight = clamp(0.45 + 0.45 * commune.democratic_quality * self.democratic_feedback - 0.25 * self.centralization)
        raw = {}
        for d in DOMAINS:
            raw[d] = max(0.005, base[d] * (1.0 - local_weight) + priority.get(d, 0.0) * local_weight)
        total = sum(raw.values())
        return {d: raw[d] / total for d in DOMAINS}


# ---------------------------------------------------------------------------
# Synthetic planet generator
# ---------------------------------------------------------------------------


BIOME_LIBRARY = {
    "equatorial_forest": {
        "soil_health": 0.78, "biodiversity": 0.92, "watershed": 0.88, "solar": 0.75,
        "wind": 0.42, "agri": 0.58, "remoteness": 0.45, "pollution": 0.22,
    },
    "temperate_mixed": {
        "soil_health": 0.72, "biodiversity": 0.63, "watershed": 0.70, "solar": 0.55,
        "wind": 0.62, "agri": 0.78, "remoteness": 0.28, "pollution": 0.34,
    },
    "drylands": {
        "soil_health": 0.43, "biodiversity": 0.48, "watershed": 0.32, "solar": 0.90,
        "wind": 0.58, "agri": 0.38, "remoteness": 0.52, "pollution": 0.25,
    },
    "coastal_delta": {
        "soil_health": 0.67, "biodiversity": 0.70, "watershed": 0.78, "solar": 0.68,
        "wind": 0.66, "agri": 0.82, "remoteness": 0.20, "pollution": 0.38,
    },
    "mountain_water": {
        "soil_health": 0.60, "biodiversity": 0.72, "watershed": 0.90, "solar": 0.62,
        "wind": 0.70, "agri": 0.42, "remoteness": 0.66, "pollution": 0.18,
    },
    "urban_corridor": {
        "soil_health": 0.42, "biodiversity": 0.32, "watershed": 0.55, "solar": 0.58,
        "wind": 0.50, "agri": 0.25, "remoteness": 0.12, "pollution": 0.55,
    },
    "steppe_grainland": {
        "soil_health": 0.66, "biodiversity": 0.54, "watershed": 0.48, "solar": 0.70,
        "wind": 0.73, "agri": 0.88, "remoteness": 0.40, "pollution": 0.24,
    },
    "subpolar_periphery": {
        "soil_health": 0.52, "biodiversity": 0.58, "watershed": 0.66, "solar": 0.35,
        "wind": 0.80, "agri": 0.22, "remoteness": 0.72, "pollution": 0.16,
    },
}

REGION_NAMES = ['Cuenca Acua Norte',
 'Cinturón Forestal Ecuatorial',
 'Comunes del Delta',
 'Anillo Templado',
 'Arco Solar Árido',
 'Torres de Agua de Montaña',
 'Comunes Cerealistas de Estepa',
 'Red Urbana de Reparación',
 'Cinturón Eólico Costero',
 'Borde de Almacenamiento Subpolar',
 'Comunes Insulares',
 'Anillo de Cuidado de Altura',
 'Malla Logística Interior',
 'Zona Agroforestal de Lluvia',
 'Asentamientos del Borde Desértico',
 'Cadena de Ciudades Fluviales']

GROUP_NAMES = ("water", "agriculture", "energy", "housing", "health", "care", "education", "logistics", "manufacturing", "storage", "governance", "knowledge", "resilience", "repair", "ecology")
SKILL_NAMES = ("infrastructure", "agriculture", "energy", "construction", "health", "care", "education", "logistics", "manufacturing", "storage", "governance", "knowledge", "resilience", "repair", "ecology", "general")


def make_cohorts(rng: random.Random, population: float, base_health: float, base_education: float, democracy: float) -> List[PopulationCohort]:
    child_share = clamp(rng.uniform(0.18, 0.28), 0.12, 0.35)
    elder_share = clamp(rng.uniform(0.10, 0.20), 0.05, 0.28)
    adult_share = max(0.45, 1.0 - child_share - elder_share)
    shares = [("children", child_share, 0.10), ("adults", adult_share, 1.0), ("elders", elder_share, 0.15)]
    cohorts = []
    for name, share, age_factor in shares:
        skill = {}
        for sk in SKILL_NAMES:
            if name == "children":
                val = base_education * rng.uniform(0.35, 0.65)
            elif name == "elders":
                val = base_education * rng.uniform(0.55, 1.05)
            else:
                val = base_education * rng.uniform(0.75, 1.25)
            skill[sk] = clamp(val, 0.05, 1.0)
        if name == "children":
            health = clamp(base_health * rng.uniform(0.90, 1.10), 0.05, 1.0)
            education = clamp(base_education * rng.uniform(0.55, 0.85), 0.05, 1.0)
        elif name == "elders":
            health = clamp(base_health * rng.uniform(0.65, 0.95), 0.05, 1.0)
            education = clamp(base_education * rng.uniform(0.85, 1.15), 0.05, 1.0)
        else:
            health = clamp(base_health * rng.uniform(0.85, 1.15), 0.05, 1.0)
            education = clamp(base_education * rng.uniform(0.85, 1.15), 0.05, 1.0)
        cohorts.append(PopulationCohort(
            name=name,
            size=population * share,
            health=health,
            education=education,
            autonomy=clamp(rng.uniform(0.55, 0.88) * (0.75 + 0.35 * democracy), 0.05, 1.0),
            trust=clamp(rng.uniform(0.45, 0.82) * (0.70 + 0.45 * democracy), 0.02, 1.0),
            skill=skill,
            age_factor=age_factor,
        ))
    return cohorts


def create_commune(rng: random.Random, region_name: str, biome: str, population: float, scenario: str) -> Commune:
    b = BIOME_LIBRARY[biome]
    base_health = clamp(rng.uniform(0.55, 0.84) - (0.06 if scenario == "scarcity_shock" else 0.0), 0.1, 1.0)
    base_education = clamp(rng.uniform(0.50, 0.86) - (0.05 if scenario == "technocratic_control" else 0.0), 0.1, 1.0)
    democracy = clamp(rng.uniform(0.45, 0.86), 0.1, 1.0)
    if scenario == "technocratic_control":
        democracy *= 0.62
    if scenario == "local_democracy":
        democracy = clamp(democracy * 1.20, 0.1, 1.0)

    cohorts = make_cohorts(rng, population, base_health, base_education, democracy)
    pop = population

    # Initial stocks/capacities. They represent normalized person-months.
    water_stock = pop * rng.uniform(0.55, 1.75) * (0.65 + b["watershed"])
    food_stock = pop * rng.uniform(0.50, 1.60) * (0.55 + b["agri"])
    energy_stock = pop * rng.uniform(0.45, 1.35) * (0.55 + 0.50 * max(b["solar"], b["wind"]))
    if scenario == "scarcity_shock":
        water_stock *= 0.70
        food_stock *= 0.68
        energy_stock *= 0.78

    shelter_capacity = pop * rng.uniform(0.78, 1.18)
    if biome == "urban_corridor":
        shelter_capacity *= rng.uniform(0.88, 1.15)
    health_cap = pop * NEED_PER_PERSON["health"] * rng.uniform(0.55, 1.25) * (0.65 + base_education)
    care_cap = pop * NEED_PER_PERSON["care"] * rng.uniform(0.60, 1.20) * (0.65 + base_health)
    edu_cap = pop * NEED_PER_PERSON["education"] * rng.uniform(0.60, 1.30) * (0.65 + base_education)
    mobility_cap = pop * NEED_PER_PERSON["mobility"] * rng.uniform(0.55, 1.25) * (1.1 - b["remoteness"])
    manufacturing_cap = pop * NEED_PER_PERSON["manufacturing"] * rng.uniform(0.45, 1.15) * (0.70 + base_education)
    storage_cap = pop * NEED_PER_PERSON["storage"] * rng.uniform(0.45, 1.30) * (0.70 + (1.0 - b["remoteness"]))
    governance_cap = pop * NEED_PER_PERSON["governance"] * rng.uniform(0.55, 1.25) * (0.65 + democracy)
    knowledge_cap = pop * NEED_PER_PERSON["knowledge"] * rng.uniform(0.45, 1.25) * (0.65 + base_education)
    resilience_cap = pop * NEED_PER_PERSON["resilience"] * rng.uniform(0.40, 1.10) * (0.65 + democracy)

    stocks = {
        "water": water_stock,
        "food": food_stock,
        "energy": energy_stock,
        "repair_materials": pop * rng.uniform(0.05, 0.22),
        "waste": pop * rng.uniform(0.06, 0.23) * (1.0 + b["pollution"]),
    }
    capacities = {
        "shelter": shelter_capacity,
        "health": health_cap,
        "care": care_cap,
        "education": edu_cap,
        "mobility": mobility_cap,
        "manufacturing": manufacturing_cap,
        "storage": storage_cap,
        "governance": governance_cap,
        "knowledge": knowledge_cap,
        "resilience": resilience_cap,
    }
    environment = {
        "soil_health": clamp(b["soil_health"] * rng.uniform(0.82, 1.12), 0.05, 1.0),
        "biodiversity": clamp(b["biodiversity"] * rng.uniform(0.78, 1.12), 0.05, 1.0),
        "watershed": clamp(b["watershed"] * rng.uniform(0.80, 1.15), 0.05, 1.0),
        "solar": clamp(b["solar"] * rng.uniform(0.90, 1.10), 0.05, 1.0),
        "wind": clamp(b["wind"] * rng.uniform(0.90, 1.10), 0.05, 1.0),
        "agri": clamp(b["agri"] * rng.uniform(0.82, 1.15), 0.05, 1.0),
        "remoteness": clamp(b["remoteness"] * rng.uniform(0.85, 1.20), 0.02, 1.0),
        "local_pollution": clamp(b["pollution"] * rng.uniform(0.80, 1.25), 0.02, 1.0),
        "renewable_infrastructure": clamp(rng.uniform(0.30, 0.70) * (0.65 + max(b["solar"], b["wind"])), 0.05, 1.0),
    }

    group_base = {}
    for g in GROUP_NAMES:
        val = rng.uniform(0.35, 0.85)
        if g == "agriculture":
            val *= 0.65 + b["agri"]
        elif g == "energy":
            val *= 0.65 + max(b["solar"], b["wind"])
        elif g == "ecology":
            val *= 0.70 + 0.35 * b["biodiversity"]
        elif g == "logistics":
            val *= 1.15 - 0.55 * b["remoteness"]
        elif g == "water":
            val *= 0.70 + 0.50 * b["watershed"]
        elif g == "manufacturing":
            val *= 0.75 + base_education
        elif g == "storage":
            val *= 0.80 + 0.25 * (1.0 - b["remoteness"])
        elif g == "governance":
            val *= 0.65 + democracy
        elif g == "knowledge":
            val *= 0.70 + base_education
        elif g == "resilience":
            val *= 0.70 + 0.25 * democracy + 0.20 * b["watershed"]
        group_base[g] = clamp(val, 0.05, 1.0)

    return Commune(
        name=("%s%s%03d" % (region_name[:9].replace(" ", ""), COMMUNE_SUFFIX, rng.randint(1, 999))),
        region_name=region_name,
        biome=biome,
        cohorts=cohorts,
        stocks=stocks,
        capacities=capacities,
        environment=environment,
        group_base=group_base,
        democratic_quality=democracy,
        truth_error=clamp(rng.uniform(0.08, 0.26) + (0.12 if scenario == "technocratic_control" else 0.0), 0.02, 0.75),
    )


def create_planet(seed: int, total_population: float, regions_count: int, communes_per_region: int, scenario: str) -> Tuple[List[Region], BoundaryState, EffectPlanner]:
    rng = random.Random(seed)
    biomes = list(BIOME_LIBRARY.keys())
    rng.shuffle(biomes)
    region_pops_raw = [lognormal_near(rng, 1.0, 0.75) for _ in range(regions_count)]
    pop_sum = sum(region_pops_raw)
    regions: List[Region] = []
    for i in range(regions_count):
        name = REGION_NAMES[i % len(REGION_NAMES)]
        if i >= len(REGION_NAMES):
            name += " %d" % (i + 1)
        biome = biomes[i % len(biomes)]
        b = BIOME_LIBRARY[biome]
        region_pop = total_population * region_pops_raw[i] / pop_sum
        commune_raw = [lognormal_near(rng, 1.0, 0.60) for _ in range(communes_per_region)]
        commune_sum = sum(commune_raw)
        communes = []
        for j in range(communes_per_region):
            cpop = region_pop * commune_raw[j] / commune_sum
            communes.append(create_commune(rng, name, biome, cpop, scenario))
        regions.append(Region(
            name=name,
            biome=biome,
            communes=communes,
            logistic_hub=clamp((1.0 - b["remoteness"]) * rng.uniform(0.70, 1.15), 0.05, 1.0),
            climate_risk=clamp(rng.uniform(0.25, 0.75) + (0.25 if biome in ("drylands", "coastal_delta") else 0.0), 0.05, 1.0),
        ))

    if scenario == "ecological_crisis":
        pressures = {
            "climate": 1.18,
            "biosphere": 1.12,
            "freshwater": 1.08,
            "soil": 1.04,
            "pollution": 1.06,
            "material_throughput": 1.10,
            "energy_throughput": 1.08,
        }
    elif scenario == "scarcity_shock":
        pressures = {
            "climate": 1.02,
            "biosphere": 0.96,
            "freshwater": 1.07,
            "soil": 0.98,
            "pollution": 0.95,
            "material_throughput": 1.03,
            "energy_throughput": 1.00,
        }
    else:
        pressures = {
            "climate": 0.96,
            "biosphere": 0.92,
            "freshwater": 0.88,
            "soil": 0.86,
            "pollution": 0.91,
            "material_throughput": 0.94,
            "energy_throughput": 0.93,
        }
    boundary = BoundaryState(pressures=pressures)

    if scenario == "technocratic_control":
        planner = EffectPlanner(democratic_feedback=0.35, centralization=0.82, privacy_pressure=0.42,
                                cooperation=0.72, redistribution_strength=0.72, climate_discipline=0.70,
                                innovation_rate=0.36, renewable_bias=0.66)
    elif scenario == "local_democracy":
        planner = EffectPlanner(democratic_feedback=0.92, centralization=0.16, privacy_pressure=0.06,
                                cooperation=0.88, redistribution_strength=0.82, climate_discipline=0.76,
                                innovation_rate=0.42, renewable_bias=0.75)
    elif scenario == "ecological_crisis":
        planner = EffectPlanner(democratic_feedback=0.78, centralization=0.34, privacy_pressure=0.12,
                                cooperation=0.86, redistribution_strength=0.88, climate_discipline=0.88,
                                innovation_rate=0.46, renewable_bias=0.84)
    elif scenario == "scarcity_shock":
        planner = EffectPlanner(democratic_feedback=0.76, centralization=0.35, privacy_pressure=0.13,
                                cooperation=0.83, redistribution_strength=0.91, climate_discipline=0.80,
                                innovation_rate=0.38, renewable_bias=0.74)
    else:
        planner = EffectPlanner()
    return regions, boundary, planner


# ---------------------------------------------------------------------------
# Simulation dynamics
# ---------------------------------------------------------------------------


@dataclass
class StepImpacts:
    step: int = 0
    impacts: Dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BOUNDARY_NAMES})
    regeneration: Dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BOUNDARY_NAMES})
    global_transfers: float = 0.0
    truth_vectors: List[TruthVector] = field(default_factory=list)
    flows: List[EffectFlow] = field(default_factory=list)
    domain_labor: Dict[str, float] = field(default_factory=lambda: {domain: 0.0 for domain in DOMAINS})
    domain_outputs: Dict[str, float] = field(default_factory=lambda: {domain: 0.0 for domain in DOMAINS})

    def add_impact(self, name: str, value: float) -> None:
        self.impacts[name] = self.impacts.get(name, 0.0) + value

    def add_regen(self, name: str, value: float) -> None:
        self.regeneration[name] = self.regeneration.get(name, 0.0) + value

    def add_labor(self, domain: str, value: float) -> None:
        self.domain_labor[domain] = self.domain_labor.get(domain, 0.0) + value

    def add_output(self, domain: str, value: float) -> None:
        self.domain_outputs[domain] = self.domain_outputs.get(domain, 0.0) + value

    def add_flow(self, flow: EffectFlow) -> None:
        self.flows.append(flow)


def flow_values(commune: Commune, domain: str) -> Dict[str, float]:
    values = commune.last_truth_values.get(domain, {})
    if values:
        return dict(values)
    return {dim: 0.0 for dim in TRUTH_DIMS}


def make_effect_flow(step: int, kind: str, legacy_term_replaced: str, action: str, domain: str,
                     source: Commune, target: Commune, activated_effect: float, note: str = "") -> EffectFlow:
    values = flow_values(target, domain)
    validity, conditions = contract_conditions_for_flow(kind, domain, values)
    score_0_4 = truth_stack_score_0_4(values)
    priority_0_1 = safe_div(score_0_4, 4.0)
    base5 = truth_stack_base5(values)
    direction = "%s=%.3f; %s=%.3f; %s=%.3f; %s=%s" % (
        LOCAL_DIRECTION_TERMS.get("angle", "angle"),
        values.get("angle_direction", 0.0),
        LOCAL_DIRECTION_TERMS.get("difference", "difference"),
        values.get("difference", 0.0),
        LOCAL_DIRECTION_TERMS.get("determination", "determination"),
        values.get("determination", 0.0),
        LOCAL_DIRECTION_TERMS.get("validity", "validity"),
        CONTRACT_VALIDITY_LABELS.get(validity, validity),
    )
    causal_link = "%s:%s→%s" % (display_domain(domain), source.name, target.name)
    return EffectFlow(
        step=step,
        kind=kind,
        legacy_term_replaced=legacy_term_replaced,
        action=action,
        domain=domain,
        sector=SECTOR_FOR_DOMAIN.get(domain, UNMAPPED_LABEL),
        from_region=source.region_name,
        from_commune=source.name,
        to_region=target.region_name,
        to_commune=target.name,
        activated_effect=max(0.0, activated_effect),
        causal_link=causal_link,
        direction_vector=direction,
        values=values,
        note=local_note(note),
        trade_object=catalog_value(domain, "trade_object"),
        meant_as=catalog_value(domain, "meant_as"),
        product_examples=catalog_value(domain, "products"),
        workplace_examples=catalog_value(domain, "workplaces"),
        service_examples=catalog_value(domain, "services"),
        ecological_clause=catalog_value(domain, "ecology"),
        climate_clause=catalog_value(domain, "climate"),
        contract_validity=CONTRACT_VALIDITY_LABELS.get(validity, validity),
        contract_conditions=conditions,
        truth_stack_score_0_4=score_0_4,
        truth_stack_priority_0_1=priority_0_1,
        truth_stack_base5=base5,
        truth_stack_decimal=truth_stack_decimal(values),
        truth_stack_compact=compact_truth_stack(values),
        dimension_meaning=dimension_meaning_summary(values),
    )

def produce_local_effects(commune: Commune, shares: Dict[str, float], boundary: BoundaryState, planner: EffectPlanner, step_impacts: StepImpacts) -> None:
    pop = commune.population()
    labor = commune.productive_time()
    boundary_penalty = boundary.penalty()
    education = commune.average_education()
    health = commune.average_health()
    cooperation = planner.cooperation * (0.65 + 0.35 * commune.average_trust())
    # A normalized labour productivity unit. 0.12 means full adult-time roughly covers monthly needs with tech/capacity factors.
    base_prod = 12.0 * labor * boundary_penalty * cooperation

    # Local effect domains. All outputs are person-month-ish normalized units.
    for domain in DOMAINS:
        domain_labor = base_prod * shares.get(domain, 0.0)
        if domain_labor <= 0.0:
            continue
        step_impacts.add_labor(domain, domain_labor)
        step_impacts.add_output(domain, domain_labor)
        step_impacts.add_flow(make_effect_flow(
            step_impacts.step,
            kind="contribution_offer",
            legacy_term_replaced="sell/labour_supply",
            action="activate_causal_effect",
            domain=domain,
            source=commune,
            target=commune,
            activated_effect=domain_labor,
            note="contribution time directed by truth-vector priority, not wage/price",
        ))
        if domain == "water":
            skill = commune.skill("infrastructure")
            watershed = commune.environment.get("watershed", 0.7)
            energy_use = 0.09 * domain_labor
            actual_energy = min(commune.stocks.get("energy", 0.0), energy_use)
            energy_factor = 0.45 + 0.55 * sat_ratio(actual_energy, energy_use)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - actual_energy
            output = domain_labor * (0.9 + 1.1 * watershed) * (0.55 + skill) * energy_factor
            commune.stocks["water"] = commune.stocks.get("water", 0.0) + output
            step_impacts.add_impact("freshwater", 0.0000000000016 * output * max(0.2, 1.1 - watershed))
            step_impacts.add_impact("energy_throughput", 0.0000000000002 * actual_energy)

        elif domain == "food":
            skill = commune.skill("agriculture")
            soil = commune.environment.get("soil_health", 0.7)
            water_need = 0.20 * domain_labor * (1.05 - 0.35 * soil)
            energy_need = 0.08 * domain_labor
            water_used = min(commune.stocks.get("water", 0.0), water_need)
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["water"] = commune.stocks.get("water", 0.0) - water_used
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            input_factor = 0.30 + 0.45 * sat_ratio(water_used, water_need) + 0.25 * sat_ratio(energy_used, energy_need)
            regenerative = clamp(0.25 + 0.45 * shares.get("ecology", 0.0) + 0.20 * planner.climate_discipline)
            output = domain_labor * (0.55 + skill) * (0.55 + commune.environment.get("agri", 0.6)) * (0.55 + soil) * input_factor
            commune.stocks["food"] = commune.stocks.get("food", 0.0) + output
            # Soil can degrade or improve depending on regenerative direction.
            commune.environment["soil_health"] = clamp(soil + 0.0015 * regenerative - 0.0018 * (1.0 - regenerative))
            step_impacts.add_impact("freshwater", 0.0000000000012 * water_used)
            step_impacts.add_impact("soil", 0.0000000000010 * output * (1.0 - regenerative))
            step_impacts.add_regen("soil", 0.0000000000011 * output * regenerative)

        elif domain == "energy":
            skill = commune.skill("energy")
            renewable = commune.environment.get("renewable_infrastructure", 0.5)
            solar_wind = max(commune.environment.get("solar", 0.5), commune.environment.get("wind", 0.5))
            repair_need = 0.10 * domain_labor * (0.85 - 0.45 * renewable)
            repair_used = min(commune.stocks.get("repair_materials", 0.0), max(0.0, repair_need))
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - repair_used
            output = domain_labor * (0.60 + skill) * (0.55 + solar_wind) * (0.70 + renewable)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) + output
            # Infrastructure improves with material and innovation.
            commune.environment["renewable_infrastructure"] = clamp(renewable + 0.0015 * planner.innovation_rate * sat_ratio(repair_used, max(repair_need, 1.0)))
            fossil_fraction = clamp((1.0 - renewable) * (1.0 - planner.renewable_bias) + 0.20 * max(0.0, boundary.pressures.get("energy_throughput", 0.9) - 1.0), 0.02, 0.65)
            step_impacts.add_impact("climate", 0.0000000000024 * output * fossil_fraction)
            step_impacts.add_impact("energy_throughput", 0.00000000000025 * output)
            step_impacts.add_impact("material_throughput", 0.0000000000010 * max(0.0, repair_need - repair_used) + 0.0000000000004 * repair_used)

        elif domain == "shelter":
            skill = commune.skill("construction")
            repair_material = commune.stocks.get("repair_materials", 0.0)
            # First reallocate/repair existing capacity; only then build.
            reuse_bias = clamp(0.55 + 0.35 * planner.sufficiency_norm + 0.25 * shares.get("repair", 0.0))
            material_need = domain_labor * (0.10 + 0.25 * (1.0 - reuse_bias))
            used_mat = min(repair_material, material_need)
            commune.stocks["repair_materials"] = repair_material - used_mat
            gained = domain_labor * (0.25 + 0.75 * reuse_bias) * (0.65 + skill) * (0.55 + sat_ratio(used_mat, max(material_need, 1.0)))
            commune.capacities["shelter"] = commune.capacities.get("shelter", 0.0) + gained
            waste_created = 0.035 * gained * (1.0 - reuse_bias)
            commune.stocks["waste"] = commune.stocks.get("waste", 0.0) + waste_created
            step_impacts.add_impact("material_throughput", 0.0000000000018 * max(0.0, material_need - used_mat) + 0.0000000000006 * used_mat)
            step_impacts.add_impact("pollution", 0.0000000000010 * waste_created)

        elif domain == "health":
            skill = commune.skill("health")
            energy_need = 0.05 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            output = domain_labor * (0.70 + skill) * (0.70 + health) * (0.65 + 0.35 * sat_ratio(energy_used, energy_need))
            commune.capacities["health"] = commune.capacities.get("health", 0.0) + output
            step_impacts.add_impact("energy_throughput", 0.00000000000018 * energy_used)

        elif domain == "care":
            skill = commune.skill("care")
            output = domain_labor * (0.75 + skill) * (0.70 + commune.average_autonomy())
            commune.capacities["care"] = commune.capacities.get("care", 0.0) + output

        elif domain == "education":
            skill = commune.skill("education")
            energy_need = 0.025 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            output = domain_labor * (0.72 + skill) * (0.70 + commune.democratic_quality) * (0.75 + 0.25 * sat_ratio(energy_used, energy_need))
            commune.capacities["education"] = commune.capacities.get("education", 0.0) + output
            step_impacts.add_impact("energy_throughput", 0.00000000000012 * energy_used)

        elif domain == "mobility":
            skill = commune.skill("logistics")
            energy_need = 0.11 * domain_labor * (0.70 + commune.environment.get("remoteness", 0.5))
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            efficiency = planner.logistics_efficiency * (0.75 + 0.25 * commune.environment.get("renewable_infrastructure", 0.5))
            output = domain_labor * (0.58 + skill) * (0.62 + efficiency) * (0.60 + 0.40 * sat_ratio(energy_used, energy_need))
            commune.capacities["mobility"] = commune.capacities.get("mobility", 0.0) + output
            carbon_intensity = (1.0 - commune.environment.get("renewable_infrastructure", 0.5)) * (1.0 - planner.renewable_bias)
            step_impacts.add_impact("climate", 0.0000000000015 * energy_used * carbon_intensity)
            step_impacts.add_impact("energy_throughput", 0.00000000000030 * energy_used)

        elif domain == "manufacturing":
            skill = commune.skill("manufacturing")
            energy_need = 0.14 * domain_labor
            material_need = 0.10 * domain_labor * (1.0 - 0.35 * shares.get("repair", 0.0))
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            material_used = min(commune.stocks.get("repair_materials", 0.0), material_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - material_used
            input_factor = 0.35 + 0.40 * sat_ratio(energy_used, energy_need) + 0.25 * sat_ratio(material_used, material_need)
            tools = domain_labor * (0.50 + skill) * input_factor
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) + 0.42 * tools
            commune.capacities["manufacturing"] = commune.capacities.get("manufacturing", 0.0) + 0.58 * tools
            step_impacts.add_impact("material_throughput", 0.0000000000014 * max(0.0, material_need - material_used) + 0.0000000000005 * material_used)
            step_impacts.add_impact("energy_throughput", 0.00000000000025 * energy_used)
            step_impacts.add_impact("pollution", 0.0000000000007 * max(0.0, tools - material_used))

        elif domain == "storage":
            skill = commune.skill("storage")
            energy_need = 0.035 * domain_labor
            material_need = 0.07 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            material_used = min(commune.stocks.get("repair_materials", 0.0), material_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - material_used
            gained = domain_labor * (0.55 + skill) * (0.55 + 0.45 * sat_ratio(material_used, material_need))
            commune.capacities["storage"] = commune.capacities.get("storage", 0.0) + gained
            # Storage reduces spoilage and grid losses by preserving basic stocks.
            protection = clamp(0.000025 * gained / max(1.0, pop))
            commune.stocks["water"] = commune.stocks.get("water", 0.0) * (1.0 + protection)
            commune.stocks["food"] = commune.stocks.get("food", 0.0) * (1.0 + protection)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) * (1.0 + 0.5 * protection)
            step_impacts.add_impact("material_throughput", 0.0000000000007 * material_used)
            step_impacts.add_impact("energy_throughput", 0.00000000000010 * energy_used)

        elif domain == "governance":
            skill = commune.skill("governance")
            output = domain_labor * (0.55 + skill) * (0.45 + commune.democratic_quality)
            commune.capacities["governance"] = commune.capacities.get("governance", 0.0) + output
            correction = 0.00000000035 * output / max(1.0, pop)
            commune.truth_error = clamp(commune.truth_error - correction * planner.democratic_feedback + 0.00003 * planner.centralization * planner.privacy_pressure)
            commune.democratic_quality = clamp(commune.democratic_quality + 0.00000000022 * output / max(1.0, pop) - 0.00002 * planner.centralization * planner.privacy_pressure)

        elif domain == "knowledge":
            skill = commune.skill("knowledge")
            energy_need = 0.020 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            output = domain_labor * (0.60 + skill) * (0.70 + commune.average_education()) * (0.70 + 0.30 * sat_ratio(energy_used, energy_need))
            commune.capacities["knowledge"] = commune.capacities.get("knowledge", 0.0) + output
            learning = 0.00000000018 * output / max(1.0, pop)
            for cohort in commune.cohorts:
                for sk in ("infrastructure", "agriculture", "energy", "construction", "health", "logistics", "manufacturing", "storage", "repair", "ecology"):
                    cohort.skill[sk] = clamp(cohort.skill.get(sk, 0.4) + learning)
            commune.environment["renewable_infrastructure"] = clamp(commune.environment.get("renewable_infrastructure", 0.5) + 0.00000000008 * output / max(1.0, pop) * planner.innovation_rate)
            step_impacts.add_impact("energy_throughput", 0.00000000000007 * energy_used)

        elif domain == "resilience":
            skill = commune.skill("resilience")
            material_need = 0.06 * domain_labor
            material_used = min(commune.stocks.get("repair_materials", 0.0), material_need)
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - material_used
            output = domain_labor * (0.55 + skill) * (0.60 + commune.democratic_quality) * (0.55 + 0.45 * sat_ratio(material_used, material_need))
            commune.capacities["resilience"] = commune.capacities.get("resilience", 0.0) + output
            # Emergency readiness creates small local buffers and lowers damage from shocks.
            commune.stocks["water"] = commune.stocks.get("water", 0.0) + 0.04 * output
            commune.stocks["food"] = commune.stocks.get("food", 0.0) + 0.03 * output
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) + 0.02 * output
            step_impacts.add_impact("material_throughput", 0.0000000000005 * material_used)

        elif domain == "repair":
            skill = commune.skill("repair")
            waste = commune.stocks.get("waste", 0.0)
            processed = min(waste, domain_labor * (0.75 + skill))
            commune.stocks["waste"] = waste - processed
            material_gain = processed * (0.42 + 0.38 * skill)
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) + material_gain
            # Repair also maintains existing capacities.
            for cap in MACRO_CAPACITY_DOMAINS:
                commune.capacities[cap] = commune.capacities.get(cap, 0.0) * (1.0 + 0.00015 * skill)
            step_impacts.add_regen("material_throughput", 0.0000000000014 * material_gain)
            step_impacts.add_regen("pollution", 0.0000000000010 * processed)

        elif domain == "ecology":
            skill = commune.skill("ecology")
            energy_need = 0.025 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            effect = domain_labor * (0.55 + skill) * (0.65 + commune.democratic_quality) * (0.65 + 0.35 * sat_ratio(energy_used, energy_need))
            commune.environment["soil_health"] = clamp(commune.environment.get("soil_health", 0.7) + 0.00000000020 * effect)
            commune.environment["biodiversity"] = clamp(commune.environment.get("biodiversity", 0.7) + 0.00000000018 * effect)
            commune.environment["watershed"] = clamp(commune.environment.get("watershed", 0.7) + 0.00000000016 * effect)
            commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) - 0.00000000016 * effect)
            step_impacts.add_regen("biosphere", 0.0000000000022 * effect)
            step_impacts.add_regen("soil", 0.0000000000018 * effect)
            step_impacts.add_regen("freshwater", 0.0000000000013 * effect)
            step_impacts.add_regen("pollution", 0.0000000000015 * effect)
            # Biosphere and soil also draw down a small share of climate pressure.
            step_impacts.add_regen("climate", 0.00000000000055 * effect)

        elif domain == "waste":
            skill = commune.skill("repair")
            waste = commune.stocks.get("waste", 0.0)
            processed = min(waste, domain_labor * (0.65 + skill))
            commune.stocks["waste"] = waste - processed
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) + processed * (0.28 + 0.28 * skill)
            commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) - 0.00000000010 * processed)
            step_impacts.add_regen("pollution", 0.0000000000012 * processed)
            step_impacts.add_regen("material_throughput", 0.0000000000008 * processed)

    # Capacity decay / maintenance burden: if not maintained, infrastructure slowly decays.
    maintenance_quality = clamp(shares.get("repair", 0.0) * 5.0 + shares.get("waste", 0.0) * 2.0 + commune.average_trust() * 0.15)
    decay = 0.0045 * (1.0 - maintenance_quality)
    for cap in MACRO_CAPACITY_DOMAINS:
        commune.capacities[cap] = max(0.0, commune.capacities.get(cap, 0.0) * (1.0 - decay))


def redistribute_planetary_commons(regions: List[Region], planner: EffectPlanner, step_impacts: StepImpacts) -> None:
    """transferencias planetarias entre regiones y comunas sin precios.

    This is what makes it a planet economy rather than a national economy:
    the algorithm checks real need and surplus globally, constrained by logistics
    and ecological cost. It does not care about national currency, exports, or GDP.
    """
    communes = [c for r in regions for c in r.communes]
    for domain in CONSUMABLE_DOMAINS:
        # Basic sufficiency target. Surplus above target can move.
        target_factor = 1.03
        donors = []
        receivers = []
        total_surplus = 0.0
        total_deficit = 0.0
        for c in communes:
            need = c.need(domain)
            stock = c.stocks.get(domain, 0.0)
            target = target_factor * need
            if stock > target:
                surplus = (stock - target) * planner.redistribution_strength
                donors.append([c, surplus])
                total_surplus += surplus
            else:
                deficit = max(0.0, need - stock)
                if deficit > 0.0:
                    priority = c.last_priorities.get(domain, 0.5)
                    receivers.append([c, deficit, priority])
                    total_deficit += deficit
        if total_surplus <= 0.0 or total_deficit <= 0.0:
            continue
        receivers.sort(key=lambda x: x[2], reverse=True)
        transfer_budget = min(total_surplus, total_deficit)
        # Global logistics capacity from mobility + logistics hubs.
        mobility_cap = sum(c.capacities.get("mobility", 0.0) for c in communes)
        mobility_need = sum(c.need("mobility") for c in communes)
        logistics_factor = clamp(sat_ratio(mobility_cap, max(mobility_need, 1.0)) * planner.logistics_efficiency)
        transfer_budget *= logistics_factor
        if transfer_budget <= 0.0:
            continue

        donor_i = 0
        for recv in receivers:
            rc, deficit, priority = recv
            if transfer_budget <= 1e-9:
                break
            want = min(deficit, transfer_budget)
            received = 0.0
            while want > 1e-9 and donor_i < len(donors):
                dc, avail = donors[donor_i]
                move = min(want, avail)
                if move <= 1e-9:
                    donor_i += 1
                    continue
                dc.stocks[domain] = dc.stocks.get(domain, 0.0) - move
                step_impacts.add_flow(make_effect_flow(
                    step_impacts.step,
                    kind="planetary_transfer",
                    legacy_term_replaced="buy/sell/import/export",
                    action="causal_transfer_to_need",
                    domain=domain,
                    source=dc,
                    target=rc,
                    activated_effect=move,
                    note="surplus and deficit matched by urgencia, not purchasing power",
                ))
                received += move
                want -= move
                transfer_budget -= move
                donors[donor_i][1] -= move
                if donors[donor_i][1] <= 1e-9:
                    donor_i += 1
            rc.stocks[domain] = rc.stocks.get(domain, 0.0) + received
            step_impacts.global_transfers += received
            # Transfer has ecological cost but is less damaging if energy system is renewable.
            if received > 0.0:
                avg_renew = mean(c.environment.get("renewable_infrastructure", 0.5) for c in communes)
                carbon = (1.0 - avg_renew) * (1.0 - planner.renewable_bias)
                step_impacts.add_impact("climate", 0.00000000000055 * received * carbon)
                step_impacts.add_impact("energy_throughput", 0.00000000000016 * received)
                step_impacts.add_impact("material_throughput", 0.00000000000020 * received)


def consume_and_update_people(commune: Commune, planner: EffectPlanner, step_impacts: Optional[StepImpacts] = None) -> None:
    satisfaction: Dict[str, float] = {}
    # Consumables: water, food, energy.
    for domain in CONSUMABLE_DOMAINS:
        need = commune.need(domain)
        stock = commune.stocks.get(domain, 0.0)
        sat = sat_ratio(stock, need)
        used = min(stock, need)
        commune.stocks[domain] = max(0.0, stock - used)
        satisfaction[domain] = sat
        if step_impacts is not None and used > 0.0:
            step_impacts.add_flow(make_effect_flow(
                step_impacts.step,
                kind="need_acceptance",
                legacy_term_replaced="buy/consumption",
                action="accept_effect_for_need",
                domain=domain,
                source=commune,
                target=commune,
                activated_effect=used,
                note="need satisfaction accepted through existence/intensity/time, not purchasing power",
            ))

    # Capacities: shelter is not consumed like food; health/care/education/mobility capacity is used this month.
    shelter_need = commune.need("shelter")
    shelter_sat = sat_ratio(commune.capacities.get("shelter", 0.0), shelter_need)
    satisfaction["shelter"] = shelter_sat
    if step_impacts is not None:
        step_impacts.add_flow(make_effect_flow(
            step_impacts.step,
            kind="need_acceptance",
            legacy_term_replaced="buy/rent",
            action="stabilize_shelter_existence",
            domain="shelter",
            source=commune,
            target=commune,
            activated_effect=min(commune.capacities.get("shelter", 0.0), shelter_need),
            note="housing access through real need and capacity, not rent/price",
        ))

    for domain in SERVICE_DOMAINS:
        need = commune.need(domain)
        cap = commune.capacities.get(domain, 0.0)
        sat = sat_ratio(cap, need)
        used = min(cap, need)
        # Service capacity partly persists as institution, partly consumed as monthly service.
        commune.capacities[domain] = max(0.0, cap - 0.72 * used)
        satisfaction[domain] = sat
        if step_impacts is not None and used > 0.0:
            step_impacts.add_flow(make_effect_flow(
                step_impacts.step,
                kind="need_acceptance",
                legacy_term_replaced="buy/service_purchase",
                action="accept_service_effect",
                domain=domain,
                source=commune,
                target=commune,
                activated_effect=used,
                note="service is used as social effect, not purchased service value",
            ))

    # Waste from consumption; lower if repair/sufficiency norms are strong.
    pop = commune.population()
    consumption_shortfall = 1.0 - mean(satisfaction.get(d, 1.0) for d in CONSUMABLE_DOMAINS)
    waste_created = pop * 0.028 * (0.65 + 0.35 * mean([satisfaction.get("food", 1.0), satisfaction.get("energy", 1.0)])) * (1.0 - 0.30 * planner.sufficiency_norm)
    # Crisis can create unmanaged waste through breakdown.
    waste_created += pop * 0.012 * consumption_shortfall
    commune.stocks["waste"] = commune.stocks.get("waste", 0.0) + waste_created
    commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) + 0.00000000005 * waste_created)

    # Update cohorts. If system is highly centralized, privacy pressure is stronger.
    privacy = clamp(planner.privacy_pressure + 0.15 * planner.centralization * (1.0 - commune.democratic_quality))
    gov_quality = clamp(0.55 * commune.democratic_quality + 0.30 * commune.average_trust() + 0.15 * (1.0 - commune.truth_error))
    for cohort in commune.cohorts:
        cohort.update_from_satisfaction(satisfaction, gov_quality, privacy)

    # Demographic dynamics: cautious and bounded. This is not a detailed population model.
    avg_sat = mean(satisfaction.values(), 0.85)
    edu = commune.average_education()
    health = commune.average_health()
    # Good conditions sustain; severe unmet basics cause contraction. Higher education moderates growth.
    monthly_growth = 0.00055 * (avg_sat - 0.62) + 0.00035 * (health - 0.55) - 0.00028 * (edu - 0.55)
    monthly_growth = clamp(monthly_growth, -0.0045, 0.0035)
    for cohort in commune.cohorts:
        cohort.size = max(0.0, cohort.size * (1.0 + monthly_growth))

    commune.last_satisfaction = satisfaction
    commune.update_truth_error(avg_sat, planner)


def simulate_step(regions: List[Region], boundary: BoundaryState, planner: EffectPlanner, step: int) -> Tuple[GlobalMetrics, List[TruthVector], StepImpacts]:
    step_impacts = StepImpacts(step=step)

    # 1) Compute truth vectors: reality -> logical stacked values -> priority.
    for region in regions:
        for commune in region.communes:
            tvs = [commune.truth_vector(domain, boundary, planner) for domain in DOMAINS]
            step_impacts.truth_vectors.extend(tvs)
            commune.last_priorities = {tv.domain: tv.priority() for tv in tvs}
            commune.last_truth_values = {tv.domain: dict(tv.values) for tv in tvs}
            shares = planner.labor_shares(tvs, commune, boundary)
            commune.last_labor_shares = shares

    # 2) Produce local effects according to truth-vector priority.
    for region in regions:
        for commune in region.communes:
            produce_local_effects(commune, commune.last_labor_shares, boundary, planner, step_impacts)

    # 3) Redistribute planetary commons: global real need and surplus, no price/currency.
    redistribute_planetary_commons(regions, planner, step_impacts)

    # 4) Consume/satisfy needs and update individuals/cohorts.
    for region in regions:
        for commune in region.communes:
            consume_and_update_people(commune, planner, step_impacts)

    # 5) actualización de límites planetarios. Añade impactos base por residuos no gestionados y contaminación local.
    total_pop = sum(r.population() for r in regions)
    total_waste = sum(c.stocks.get("waste", 0.0) for r in regions for c in r.communes)
    avg_local_pollution = weighted_mean(((c.environment.get("local_pollution", 0.2), c.population()) for r in regions for c in r.communes), default=0.2)
    avg_soil_gap = weighted_mean(((1.0 - c.environment.get("soil_health", 0.7), c.population()) for r in regions for c in r.communes), default=0.3)
    avg_bio_gap = weighted_mean(((1.0 - c.environment.get("biodiversity", 0.7), c.population()) for r in regions for c in r.communes), default=0.3)
    step_impacts.add_impact("pollution", 0.00000000000035 * total_waste + 0.0008 * max(0.0, avg_local_pollution - 0.55))
    step_impacts.add_impact("soil", 0.0005 * max(0.0, avg_soil_gap - 0.30))
    step_impacts.add_impact("biosphere", 0.0005 * max(0.0, avg_bio_gap - 0.30))
    # Sufficiency and climate discipline slowly lower systemic pressure.
    step_impacts.add_regen("material_throughput", 0.0020 * planner.sufficiency_norm * mean((c.average_trust() for r in regions for c in r.communes), default=0.5))
    step_impacts.add_regen("energy_throughput", 0.0030 * planner.sufficiency_norm * planner.renewable_bias)
    step_impacts.add_regen("climate", 0.0009 * planner.climate_discipline * planner.renewable_bias)

    boundary.apply_impacts(step_impacts.impacts, step_impacts.regeneration)

    metrics = collect_metrics(regions, boundary, step, step_impacts.global_transfers)
    return metrics, step_impacts.truth_vectors, step_impacts


def collect_metrics(regions: List[Region], boundary: BoundaryState, step: int, transfers: float) -> GlobalMetrics:
    communes = [c for r in regions for c in r.communes]
    total_pop = sum(c.population() for c in communes)
    # Wellbeing from satisfaction, health, autonomy, trust, and ecological safety.
    wellbeing_items = []
    unmet_items = []
    basic_buffer_items = []
    resilience_items = []
    for c in communes:
        sat = c.last_satisfaction or {d: 0.8 for d in ("water", "food", "energy", "shelter", "health", "care", "education", "mobility", "governance", "knowledge", "resilience")}
        basic_sat = 0.30 * sat.get("water", 1.0) + 0.30 * sat.get("food", 1.0) + 0.18 * sat.get("shelter", 1.0) + 0.12 * sat.get("energy", 1.0) + 0.10 * sat.get("health", 1.0)
        civic_sat = 0.36 * sat.get("governance", 1.0) + 0.34 * sat.get("knowledge", 1.0) + 0.30 * sat.get("resilience", 1.0)
        freedom = 0.55 * c.average_autonomy() + 0.45 * c.average_trust()
        ecological_safety = boundary.penalty()
        wellbeing = clamp(0.50 * basic_sat + 0.17 * freedom + 0.11 * c.average_health() + 0.10 * civic_sat + 0.12 * ecological_safety)
        wellbeing_items.append((wellbeing, c.population()))
        unmet_basic = 1.0 - clamp(0.35 * sat.get("water", 1.0) + 0.35 * sat.get("food", 1.0) + 0.15 * sat.get("shelter", 1.0) + 0.15 * sat.get("health", 1.0))
        unmet_items.append((unmet_basic, c.population()))
        basic_need = max(1.0, c.need("water") + c.need("food") + c.need("energy"))
        basic_stock = c.stocks.get("water", 0.0) + c.stocks.get("food", 0.0) + c.stocks.get("energy", 0.0)
        basic_buffer_items.append((safe_div(basic_stock, basic_need, 0.0), c.population()))
        resilience = clamp(0.40 * sat_ratio(c.capacities.get("resilience", 0.0), max(1.0, c.need("resilience"))) +
                           0.25 * sat_ratio(c.capacities.get("storage", 0.0), max(1.0, c.need("storage"))) +
                           0.20 * sat_ratio(basic_stock, 1.20 * basic_need) +
                           0.15 * boundary.penalty())
        resilience_items.append((resilience, c.population()))
    worst_name, worst_pressure = boundary.worst()
    waste_stock = sum(c.stocks.get("waste", 0.0) for c in communes)
    repair_materials = sum(c.stocks.get("repair_materials", 0.0) for c in communes)
    food_stock = sum(c.stocks.get("food", 0.0) for c in communes)
    water_stock = sum(c.stocks.get("water", 0.0) for c in communes)
    energy_stock = sum(c.stocks.get("energy", 0.0) for c in communes)
    contribution_time = sum(c.productive_time() for c in communes)
    macro_capacity = sum(c.capacities.get(domain, 0.0) for c in communes for domain in MACRO_CAPACITY_DOMAINS)
    avg_truth_error = weighted_mean(((c.truth_error, c.population()) for c in communes), default=0.0)
    avg_democracy = weighted_mean(((c.democratic_quality, c.population()) for c in communes), default=0.0)
    avg_trust = weighted_mean(((c.average_trust(), c.population()) for c in communes), default=0.0)
    circularity_index = clamp(repair_materials / max(1.0, repair_materials + waste_stock))
    coordination_quality = clamp(0.36 * avg_democracy + 0.34 * avg_trust + 0.30 * (1.0 - avg_truth_error))
    basic_buffer_months = weighted_mean(basic_buffer_items, default=0.0)
    resilience_index = weighted_mean(resilience_items, default=0.0)
    satisfaction_inequality = weighted_gini(wellbeing_items)
    planetary_reproduction_index = clamp(0.30 * weighted_mean(wellbeing_items, default=0.0) +
                                         0.22 * (1.0 - weighted_mean(unmet_items, default=0.0)) +
                                         0.18 * boundary.penalty() +
                                         0.12 * circularity_index +
                                         0.10 * coordination_quality +
                                         0.08 * resilience_index)
    return GlobalMetrics(
        step=step,
        population=total_pop,
        wellbeing=weighted_mean(wellbeing_items, default=0.0),
        unmet_basic=weighted_mean(unmet_items, default=0.0),
        avg_trust=avg_trust,
        avg_autonomy=weighted_mean(((c.average_autonomy(), c.population()) for c in communes), default=0.0),
        avg_health=weighted_mean(((c.average_health(), c.population()) for c in communes), default=0.0),
        avg_education=weighted_mean(((c.average_education(), c.population()) for c in communes), default=0.0),
        avg_truth_error=avg_truth_error,
        overshoot=boundary.overshoot(),
        mean_boundary_pressure=boundary.mean_pressure(),
        worst_boundary=worst_name,
        worst_boundary_pressure=worst_pressure,
        waste_stock=waste_stock,
        repair_materials=repair_materials,
        food_stock=food_stock,
        water_stock=water_stock,
        energy_stock=energy_stock,
        global_transfers=transfers,
        contribution_time=contribution_time,
        contribution_time_per_person=safe_div(contribution_time, total_pop, 0.0),
        satisfaction_inequality=satisfaction_inequality,
        resilience_index=resilience_index,
        circularity_index=circularity_index,
        coordination_quality=coordination_quality,
        basic_buffer_months=basic_buffer_months,
        macro_capacity=macro_capacity,
        planetary_reproduction_index=planetary_reproduction_index,
    )


def collect_macro_accounts(regions: List[Region], boundary: BoundaryState, step: int, step_impacts: Optional[StepImpacts] = None) -> List[MacroAccountRow]:
    """Global accounts for a planet economy.

    These rows are analogous to national accounts, sector accounts, labour accounts,
    public-goods accounts and external-sector accounts, but without money, prices,
    income, profit or GDP. The core balance is need/available/difference/effect.
    """
    communes = [c for r in regions for c in r.communes]
    rows: List[MacroAccountRow] = []
    flow_counts: Dict[str, int] = {domain: 0 for domain in DOMAINS}
    if step_impacts is not None:
        for flow in step_impacts.flows:
            flow_counts[flow.domain] = flow_counts.get(flow.domain, 0) + 1
    total_labor = sum(step_impacts.domain_labor.values()) if step_impacts is not None else 0.0
    for domain in DOMAINS:
        need = 0.0
        available = 0.0
        stock_or_capacity = 0.0
        priority_items = []
        labor_share_items = []
        truth_error_items = []
        democracy_items = []
        for c in communes:
            pop = c.population()
            if domain == "ecology":
                n = c.ecology_need()
                a = c.available_for_need(domain)
            elif domain == "waste":
                n = c.waste_need()
                a = max(0.0, c.waste_need() - c.stocks.get("waste", 0.0))
            else:
                n = c.need(domain)
                a = c.available_for_need(domain)
            need += n
            available += a
            if domain in CONSUMABLE_DOMAINS:
                stock_or_capacity += c.stocks.get(domain, 0.0)
            elif domain == "repair":
                stock_or_capacity += c.stocks.get("repair_materials", 0.0)
            elif domain == "waste":
                stock_or_capacity += c.stocks.get("waste", 0.0)
            elif domain in MACRO_CAPACITY_DOMAINS:
                stock_or_capacity += c.capacities.get(domain, 0.0)
            priority_items.append((c.last_priorities.get(domain, 0.0), pop))
            labor_share_items.append((c.last_labor_shares.get(domain, 0.0), pop))
            truth_error_items.append((c.truth_error, pop))
            democracy_items.append((c.democratic_quality, pop))
        gap = normalized_need_gap(need, available)
        satisfaction = sat_ratio(available, need)
        contribution_time = 0.0
        if step_impacts is not None:
            contribution_time = step_impacts.domain_labor.get(domain, 0.0)
        rows.append(MacroAccountRow(
            step=step,
            domain=domain,
            sector=SECTOR_FOR_DOMAIN.get(domain, "unmapped"),
            need=need,
            available=available,
            gap=gap,
            satisfaction=satisfaction,
            priority=weighted_mean(priority_items, default=0.0),
            labor_share=weighted_mean(labor_share_items, default=safe_div(contribution_time, total_labor, 0.0)),
            contribution_time=contribution_time,
            stock_or_capacity=stock_or_capacity,
            boundary_penalty=boundary.penalty(),
            truth_error=weighted_mean(truth_error_items, default=0.0),
            democratic_quality=weighted_mean(democracy_items, default=0.0),
            activated_flows=flow_counts.get(domain, 0),
        ))
    return rows


def run_simulation(seed: int, steps: int, population: float, regions_count: int, communes_per_region: int, scenario: str) -> Tuple[List[Region], BoundaryState, EffectPlanner, List[GlobalMetrics], List[TruthVector], List[MacroAccountRow], List[EffectFlow]]:
    regions, boundary, planner = create_planet(seed, population, regions_count, communes_per_region, scenario)
    timeline: List[GlobalMetrics] = []
    macro_accounts: List[MacroAccountRow] = []
    last_truth: List[TruthVector] = []
    last_flows: List[EffectFlow] = []
    # Initial metrics with no consumption history yet.
    timeline.append(collect_metrics(regions, boundary, 0, 0.0))
    macro_accounts.extend(collect_macro_accounts(regions, boundary, 0, None))
    for step in range(1, steps + 1):
        metrics, truth_vectors, step_impacts = simulate_step(regions, boundary, planner, step)
        timeline.append(metrics)
        macro_accounts.extend(collect_macro_accounts(regions, boundary, step, step_impacts))
        last_truth = truth_vectors
        last_flows = step_impacts.flows
    return regions, boundary, planner, timeline, last_truth, macro_accounts, last_flows


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def ensure_dir(path: str) -> None:
    if not path:
        return
    if not os.path.exists(path):
        os.makedirs(path)


def write_timeline(path: str, timeline: List[GlobalMetrics]) -> None:
    rows = [m.as_row() for m in timeline]
    write_dict_rows_localized(path, rows, list(rows[0].keys()))


def write_communes(path: str, regions: List[Region]) -> None:
    fields = [
        "region", "commune", "biome", "population", "wellbeing_proxy", "avg_health", "avg_education",
        "avg_autonomy", "avg_trust", "truth_error", "democratic_quality",
        "water_stock", "food_stock", "energy_stock", "shelter_capacity", "health_capacity",
        "care_capacity", "education_capacity", "mobility_capacity", "manufacturing_capacity",
        "storage_capacity", "governance_capacity", "knowledge_capacity", "resilience_capacity",
        "repair_materials", "waste",
        "soil_health", "biodiversity", "watershed", "local_pollution", "renewable_infrastructure",
        "top_priority_domain", "top_priority", "top_labor_domain", "top_labor_share",
    ]
    rows: List[Dict[str, object]] = []
    for r in regions:
        for c in r.communes:
            sat = c.last_satisfaction or {}
            wellbeing_proxy = clamp(0.55 * mean(sat.values(), 0.8) + 0.15 * c.average_health() + 0.15 * c.average_autonomy() + 0.15 * c.average_trust())
            top_priority = max(c.last_priorities.items(), key=lambda kv: kv[1]) if c.last_priorities else ("none", 0.0)
            top_labor = max(c.last_labor_shares.items(), key=lambda kv: kv[1]) if c.last_labor_shares else ("none", 0.0)
            rows.append({
                "region": r.name,
                "commune": c.name,
                "biome": c.biome,
                "population": round(c.population(), 3),
                "wellbeing_proxy": round(wellbeing_proxy, 6),
                "avg_health": round(c.average_health(), 6),
                "avg_education": round(c.average_education(), 6),
                "avg_autonomy": round(c.average_autonomy(), 6),
                "avg_trust": round(c.average_trust(), 6),
                "truth_error": round(c.truth_error, 6),
                "democratic_quality": round(c.democratic_quality, 6),
                "water_stock": round(c.stocks.get("water", 0.0), 3),
                "food_stock": round(c.stocks.get("food", 0.0), 3),
                "energy_stock": round(c.stocks.get("energy", 0.0), 3),
                "shelter_capacity": round(c.capacities.get("shelter", 0.0), 3),
                "health_capacity": round(c.capacities.get("health", 0.0), 3),
                "care_capacity": round(c.capacities.get("care", 0.0), 3),
                "education_capacity": round(c.capacities.get("education", 0.0), 3),
                "mobility_capacity": round(c.capacities.get("mobility", 0.0), 3),
                "manufacturing_capacity": round(c.capacities.get("manufacturing", 0.0), 3),
                "storage_capacity": round(c.capacities.get("storage", 0.0), 3),
                "governance_capacity": round(c.capacities.get("governance", 0.0), 3),
                "knowledge_capacity": round(c.capacities.get("knowledge", 0.0), 3),
                "resilience_capacity": round(c.capacities.get("resilience", 0.0), 3),
                "repair_materials": round(c.stocks.get("repair_materials", 0.0), 3),
                "waste": round(c.stocks.get("waste", 0.0), 3),
                "soil_health": round(c.environment.get("soil_health", 0.0), 6),
                "biodiversity": round(c.environment.get("biodiversity", 0.0), 6),
                "watershed": round(c.environment.get("watershed", 0.0), 6),
                "local_pollution": round(c.environment.get("local_pollution", 0.0), 6),
                "renewable_infrastructure": round(c.environment.get("renewable_infrastructure", 0.0), 6),
                "top_priority_domain": top_priority[0],
                "top_priority": round(top_priority[1], 6),
                "top_labor_domain": top_labor[0],
                "top_labor_share": round(top_labor[1], 6),
            })
    write_dict_rows_localized(path, rows, fields)


def write_truth_audit(path: str, truth_vectors: List[TruthVector], step: int, limit: int = 500) -> None:
    if not truth_vectors:
        return
    ordered = sorted(truth_vectors, key=lambda tv: tv.priority(), reverse=True)[:limit]
    rows = [tv.as_row(step) for tv in ordered]
    write_dict_rows_localized(path, rows, list(rows[0].keys()))


def write_macro_accounts(path: str, rows: List[MacroAccountRow]) -> None:
    if not rows:
        return
    data = [r.as_row() for r in rows]
    write_dict_rows_localized(path, data, list(data[0].keys()))


def write_effect_flows(path: str, flows: List[EffectFlow], limit: int = 20000) -> None:
    if not flows:
        return
    selected = flows[:limit]
    rows = [f.as_row() for f in selected]
    write_dict_rows_localized(path, rows, list(rows[0].keys()))


def write_dimension_guide(path: str) -> None:
    fields = ["dimension", "name", "short", "question", "contract_role", "economic_replacement", "weight"]
    rows: List[Dict[str, object]] = []
    for dim in TRUTH_DIMS:
        item = DIMENSION_GUIDE[dim]
        rows.append({
            "dimension": item["name"],
            "name": item["name"],
            "short": item["short"],
            "question": item["question"],
            "contract_role": item["contract_role"],
            "economic_replacement": item["economic_replacement"],
            "weight": TRUTH_WEIGHTS.get(dim, 0.0),
        })
    write_dict_rows_localized(path, rows, fields)


def write_trade_dimension_catalog(path: str) -> None:
    fields = ["domain", "sector", "trade_object", "meant_as", "products", "workplaces", "services", "ecology", "climate"]
    rows: List[Dict[str, object]] = []
    for domain in DOMAINS:
        item = TRADE_CATALOG[domain]
        rows.append({
            "domain": domain,
            "sector": SECTOR_FOR_DOMAIN.get(domain, UNMAPPED_LABEL),
            "trade_object": item["trade_object"],
            "meant_as": item["meant_as"],
            "products": item["products"],
            "workplaces": item["workplaces"],
            "services": item["services"],
            "ecology": item["ecology"],
            "climate": item["climate"],
        })
    write_dict_rows_localized(path, rows, fields)


def md_escape(value: object) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def shorten(value: object, limit: int = 140) -> str:
    text = str(value)
    if len(text) <= limit:
        return text
    return text[:max(0, limit - 1)].rstrip() + "…"


def write_trade_contracts_report(path: str, flows: List[EffectFlow], truth_vectors: List[TruthVector], timeline: List[GlobalMetrics], limit: int = 120) -> None:
    lines: List[str] = []
    lines.append('# Comercio en dimensiones: contrato, apilamiento de verdad, efecto')
    lines.append("")
    lines.append('Este protocolo muestra cómo compra, venta, importación, exportación, mercado laboral, mercado de productos y mercado de servicios son sustituidos en la simulación.')
    lines.append("")
    lines.append('**Forma antigua:** mercancía + cantidad + precio + propiedad → compra/venta')
    lines.append("")
    lines.append('**Forma nueva:** causalidad + tiempo + intensidad + existencia + potencias + efectos + sustancia + materia + diferencia + determinación + fenómenos + dirección angular → contrato de efecto')
    lines.append("")
    lines.append('El valor de verdad apilado es el estado de doce dimensiones de un comercio. Cada dimensión está en 0..4. El apilamiento base cinco contiene una cifra por dimensión; la puntuación no es dinero, sino una cifra de prioridad y validez.')
    lines.append("")
    lines.append('## Dimensiones')
    lines.append("")
    lines.append("| %s | %s | %s | %s |" % ('abreviatura', 'dimensión', 'pregunta contractual', 'sustitución económica'))
    lines.append("|---|---|---|---|")
    for dim in TRUTH_DIMS:
        g = DIMENSION_GUIDE[dim]
        lines.append("| %s | %s | %s | %s |" % (md_escape(g["short"]), md_escape(g["name"]), md_escape(g["question"]), md_escape(g["economic_replacement"])))
    lines.append("")
    lines.append('## Lo comerciado: productos, puestos de trabajo, servicios, ecología, clima')
    lines.append("")
    lines.append("| %s | %s | %s | %s | %s | %s |" % ('dominio', 'efecto comerciado', 'productos', 'puestos de trabajo', 'servicios', 'cláusula ecológica y climática'))
    lines.append("|---|---|---|---|---|---|")
    for domain in DOMAINS:
        cat = TRADE_CATALOG[domain]
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            md_escape(display_domain(domain)),
            md_escape(cat["trade_object"]),
            md_escape(cat["products"]),
            md_escape(cat["workplaces"]),
            md_escape(cat["services"]),
            md_escape(cat["ecology"] + " / " + cat["climate"]),
        ))
    lines.append("")
    lines.append('## Contratos de efecto de ejemplo del último paso de simulación')
    lines.append("")
    lines.append('Un contrato es una liberación condicional de efecto. Dice que una acción puede o debe suceder porque su apilamiento de verdad muestra una brecha real, una causa, una condición temporal, una condición de sustancia, una determinación social y una dirección angular.')
    lines.append("")
    headers = [localized_label("contract"), localized_label("old_form"), localized_label("domain"), localized_label("what"), localized_label("meant"), localized_label("validity"), localized_label("base5"), localized_label("score"), localized_label("conditions")]
    lines.append("| " + " | ".join(md_escape(h) for h in headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for flow in sorted(flows, key=lambda f: (f.truth_stack_priority_0_1, f.activated_effect), reverse=True)[:limit]:
        validity = CONTRACT_VALIDITY_LABELS.get(flow.contract_validity, flow.contract_validity)
        row = [
            display_kind(flow.kind),
            display_legacy(flow.legacy_term_replaced),
            display_domain(flow.domain),
            flow.trade_object,
            flow.meant_as,
            validity,
            flow.truth_stack_base5,
            "%.3f" % flow.truth_stack_score_0_4,
            flow.contract_conditions,
        ]
        lines.append("| " + " | ".join(md_escape(x) for x in row) + " |")
    lines.append("")
    lines.append('## Cómo el apilamiento se relaciona con las dimensiones')
    lines.append("")
    for item in ['Cada dimensión mide otro aspecto de la realidad: causa, urgencia, fuerza, existencia, posibilidad, consecuencia, material, lugar, brecha, legitimación, aparición y dirección.', 'El apilamiento base cinco guarda las cifras redondeadas en el orden dimensional.', 'La puntuación solo ayuda a ordenar. Las cifras individuales siguen decidiendo el contrato.', 'Alta diferencia con baja dirección angular significa: la necesidad es real, pero la acción debe rediseñarse o bloquearse.']:
        lines.append("- " + item)
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def write_summary(path: str, regions: List[Region], boundary: BoundaryState, planner: EffectPlanner, timeline: List[GlobalMetrics], scenario: str, seed: int) -> None:
    first = timeline[0]
    last = timeline[-1]
    planner_summary = {
        local_field("democratic_quality"): getattr(planner, "democratic_feedback", None),
        local_field("coordination_quality"): getattr(planner, "cooperation", None),
        local_field("overshoot"): getattr(planner, "climate_discipline", None),
        local_field("resilience_index"): getattr(planner, "redistribution_strength", None),
    }
    summary = {
        local_summary_key("model"): 'Simulación conceptual de economía planetaria de efectos',
        local_summary_key("scenario"): scenario,
        local_summary_key("seed"): seed,
        local_summary_key("steps"): len(timeline) - 1,
        local_summary_key("regions"): len(regions),
        local_summary_key("communes"): sum(len(r.communes) for r in regions),
        local_summary_key("initial"): localize_metric_row(first.as_row()),
        local_summary_key("final"): localize_metric_row(last.as_row()),
        local_summary_key("delta"): {
            local_field("wellbeing"): round(last.wellbeing - first.wellbeing, 6),
            local_field("unmet_basic"): round(last.unmet_basic - first.unmet_basic, 6),
            local_field("overshoot"): round(last.overshoot - first.overshoot, 6),
            local_field("avg_trust"): round(last.avg_trust - first.avg_trust, 6),
            local_field("avg_autonomy"): round(last.avg_autonomy - first.avg_autonomy, 6),
            local_field("avg_truth_error"): round(last.avg_truth_error - first.avg_truth_error, 6),
            local_field("planetary_reproduction_index"): round(last.planetary_reproduction_index - first.planetary_reproduction_index, 6),
            local_field("resilience_index"): round(last.resilience_index - first.resilience_index, 6),
            local_field("coordination_quality"): round(last.coordination_quality - first.coordination_quality, 6),
        },
        local_summary_key("boundary_pressures"): {display_boundary(k): v for k, v in boundary.pressures.items()},
        local_summary_key("planner"): planner_summary,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, sort_keys=True)

def interpretation(first: GlobalMetrics, last: GlobalMetrics) -> str:
    parts = []
    if last.wellbeing > first.wellbeing + 0.02:
        parts.append("general_improvement")
    elif last.wellbeing < first.wellbeing - 0.02:
        parts.append("general_deterioration")
    else:
        parts.append("mixed_or_stable")
    if last.overshoot < first.overshoot - 0.02:
        parts.append("planetary_overshoot_reduced")
    elif last.overshoot > first.overshoot + 0.02:
        parts.append("planetary_overshoot_increased")
    else:
        parts.append("planetary_boundaries_roughly_stable")
    if last.avg_truth_error < first.avg_truth_error:
        parts.append("truth_feedback_improved")
    else:
        parts.append("truth_feedback_not_improved")
    if last.avg_autonomy < first.avg_autonomy - 0.02:
        parts.append("freedom_warning")
    return ", ".join(parts)


def write_manifest(path: str, timeline: List[GlobalMetrics], boundary: BoundaryState, scenario: str) -> None:
    first = timeline[0]
    last = timeline[-1]
    lines: List[str] = []
    lines.append('# Simulación de economía planetaria: economía de efectos ampliada')
    lines.append("")
    lines.append('Esta simulación no modela una economía nacional con dinero, precios, producto interno bruto, salarios, ganancia, renta o valores de comercio exterior.')
    lines.append('Modela una economía planetaria de efectos: necesidades, materiales, potencias, límites ecológicos, contribuciones de tiempo, capacidades, sectores y retroalimentación social.')
    lines.append("")
    lines.append('## Principio central')
    lines.append("")
    lines.append('Una acción económica no es aquí una transacción de compra o venta, sino un cambio de estado:')
    lines.append("")
    lines.append("```")
    lines.append('fenómeno + causalidad + tiempo + intensidad + existencia + potencias + efectos + sustancia + materia + diferencia + determinación + fenómenos + dirección angular → contrato de efecto → realidad cambiada')
    lines.append("```")
    lines.append("")
    lines.append('## Estado final')
    lines.append("")
    lines.append("- %s: %s" % ('Escenario', scenario))
    lines.append("- %s: %.4f → %.4f" % (localized_label("wellbeing"), first.wellbeing, last.wellbeing))
    lines.append("- %s: %.4f → %.4f" % (localized_label("unmet"), first.unmet_basic, last.unmet_basic))
    lines.append("- %s: %.4f → %.4f" % (localized_label("overshoot"), first.overshoot, last.overshoot))
    lines.append("- %s: %.4f → %.4f" % (localized_label("truth_error"), first.avg_truth_error, last.avg_truth_error))
    lines.append("- %s: %.4f → %.4f" % (localized_label("autonomy"), first.avg_autonomy, last.avg_autonomy))
    lines.append("- %s: %s = %.3f" % (localized_label("worst_boundary"), display_boundary(last.worst_boundary), last.worst_boundary_pressure))
    lines.append("")
    lines.append('## Interpretación')
    lines.append("")
    lines.append('La mejora significa menos sufrimiento evitable, mejor cobertura de necesidades básicas, menor exceso, más resiliencia, mejor corrección de verdad y más autonomía real.')
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

# ---------------------------------------------------------------------------
# Terminal display: visible trade in dimensions
# ---------------------------------------------------------------------------


TERMINAL_COLOR_ENABLED = True


def set_terminal_color_enabled(enabled: bool) -> None:
    global TERMINAL_COLOR_ENABLED
    TERMINAL_COLOR_ENABLED = bool(enabled)


def ansi_wrap(text: object, *codes: str) -> str:
    raw = str(text)
    if not TERMINAL_COLOR_ENABLED or not codes:
        return raw
    return "".join(codes) + raw + "\033[0m"


def ansi_fg(r: int, g: int, b: int) -> str:
    return "\033[38;2;%d;%d;%dm" % (int(r), int(g), int(b))


def ansi_bg(r: int, g: int, b: int) -> str:
    return "\033[48;2;%d;%d;%dm" % (int(r), int(g), int(b))


ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_ITALIC = "\033[3m"
ANSI_UNDERLINE = "\033[4m"


DIMENSION_THEME = {
    "causality": {"fg": (255, 87, 87), "bg": (70, 10, 16), "symbol": "⚙", "glow": (255, 196, 196)},
    "time": {"fg": (255, 166, 0), "bg": (82, 45, 0), "symbol": "⏳", "glow": (255, 220, 150)},
    "intensity": {"fg": (255, 214, 10), "bg": (92, 72, 0), "symbol": "🔥", "glow": (255, 245, 170)},
    "existence": {"fg": (38, 222, 129), "bg": (9, 64, 33), "symbol": "●", "glow": (186, 255, 221)},
    "potencies": {"fg": (161, 108, 255), "bg": (49, 20, 92), "symbol": "✦", "glow": (227, 205, 255)},
    "effects": {"fg": (0, 245, 212), "bg": (0, 64, 58), "symbol": "↺", "glow": (180, 255, 244)},
    "substance": {"fg": (190, 140, 90), "bg": (72, 44, 20), "symbol": "▣", "glow": (240, 210, 180)},
    "matter": {"fg": (120, 185, 255), "bg": (20, 45, 79), "symbol": "⬢", "glow": (205, 231, 255)},
    "difference": {"fg": (255, 46, 138), "bg": (84, 9, 50), "symbol": "Δ", "glow": (255, 195, 224)},
    "determination": {"fg": (58, 134, 255), "bg": (12, 34, 86), "symbol": "⚖", "glow": (198, 224, 255)},
    "phenomena": {"fg": (255, 106, 188), "bg": (76, 11, 53), "symbol": "◉", "glow": (255, 210, 235)},
    "angle_direction": {"fg": (0, 229, 255), "bg": (0, 56, 69), "symbol": "🧭", "glow": (188, 250, 255)},
}


def dim_theme(dim: str) -> Dict[str, object]:
    return DIMENSION_THEME.get(dim, {"fg": (255, 255, 255), "bg": (40, 40, 40), "symbol": "•", "glow": (230, 230, 230)})


def color_text(text: object, fg: Optional[Tuple[int, int, int]] = None, bg: Optional[Tuple[int, int, int]] = None, bold: bool = False, italic: bool = False, underline: bool = False, dimmed: bool = False) -> str:
    codes: List[str] = []
    if bold:
        codes.append(ANSI_BOLD)
    if italic:
        codes.append(ANSI_ITALIC)
    if underline:
        codes.append(ANSI_UNDERLINE)
    if dimmed:
        codes.append(ANSI_DIM)
    if fg is not None:
        codes.append(ansi_fg(*fg))
    if bg is not None:
        codes.append(ansi_bg(*bg))
    return ansi_wrap(text, *codes)


def rainbow_text(text: str) -> str:
    palette = [
        (255, 87, 87), (255, 166, 0), (255, 214, 10), (38, 222, 129),
        (0, 245, 212), (58, 134, 255), (161, 108, 255), (255, 46, 138),
        (0, 229, 255), (255, 106, 188),
    ]
    if not TERMINAL_COLOR_ENABLED:
        return text
    out: List[str] = []
    for i, ch in enumerate(text):
        if ch.isspace():
            out.append(ch)
        else:
            out.append(color_text(ch, fg=palette[i % len(palette)], bold=True))
    return "".join(out)


def styled_badge(text: str, fg: Tuple[int, int, int], bg: Tuple[int, int, int], bold: bool = True) -> str:
    return color_text(" %s " % text, fg=fg, bg=bg, bold=bold)


def color_dim_short(short: str) -> str:
    for dim in TRUTH_DIMS:
        if DIMENSION_GUIDE[dim]["short"] == short:
            theme = dim_theme(dim)
            return styled_badge(short, theme["fg"], theme["bg"])
    return short


def render_dim_meter(value: float, dim: str, width: int = 10) -> str:
    theme = dim_theme(dim)
    ratio = max(0.0, min(1.0, value / 4.0))
    filled = int(round(ratio * width))
    filled = max(0, min(width, filled))
    full = color_text("█" * filled, fg=theme["fg"], bold=True) if filled > 0 else ""
    rest = color_text("░" * (width - filled), fg=(95, 95, 95)) if width - filled > 0 else ""
    return full + rest


def render_truth_stack_badges(values: Dict[str, float]) -> str:
    parts: List[str] = []
    for dim in TRUTH_DIMS:
        guide = DIMENSION_GUIDE[dim]
        theme = dim_theme(dim)
        digit = truth_digit(values.get(dim, 0.0))
        label = "%s%s=%d" % (theme["symbol"], guide["short"], digit)
        parts.append(styled_badge(label, theme["fg"], theme["bg"]))
    return " ".join(parts)


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")
ANSI_RESET = "\033[0m"


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


def terminal_char_width(ch: str) -> int:
    """Small stdlib-only display width estimator for UTF-8 terminal output."""
    if not ch:
        return 0
    code = ord(ch)
    if ch in "\n\r\t":
        return 0 if ch != "\t" else 4
    if unicodedata.combining(ch):
        return 0
    # Emoji blocks are commonly rendered double-width.
    if (
        0x1F000 <= code <= 0x1FAFF
        or 0x2600 <= code <= 0x27BF
    ):
        return 2
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def terminal_visible_width(text: str) -> int:
    clean = strip_ansi(str(text))
    return sum(terminal_char_width(ch) for ch in clean)


def terminal_columns() -> int:
    if FORCED_TERMINAL_WIDTH > 0:
        return max(40, int(FORCED_TERMINAL_WIDTH))
    return max(40, shutil.get_terminal_size((118, 24)).columns)



def terminal_content_width(extra_margin: int = 0) -> int:
    return max(30, terminal_columns() - max(0, extra_margin))


def plain_wrap(text: str, width: int) -> List[str]:
    """Word-wrap plain text by terminal display width, without external deps."""
    width = max(8, width)
    words = str(text).replace("\n", " ").split(" ")
    lines: List[str] = []
    line = ""
    for word in words:
        if word == "":
            continue
        if terminal_visible_width(word) > width:
            if line:
                lines.append(line.rstrip())
                line = ""
            chunk = ""
            chunk_w = 0
            for ch in word:
                cw = terminal_char_width(ch)
                if chunk_w + cw > width and chunk:
                    lines.append(chunk)
                    chunk = ""
                    chunk_w = 0
                chunk += ch
                chunk_w += cw
            if chunk:
                line = chunk + " "
            continue
        candidate = (line + word + " ") if line else (word + " ")
        if terminal_visible_width(candidate.rstrip()) <= width:
            line = candidate
        else:
            if line:
                lines.append(line.rstrip())
            line = word + " "
    if line:
        lines.append(line.rstrip())
    return lines or [""]


def _ansi_active_codes_until(text: str) -> List[str]:
    active: List[str] = []
    for seq in ANSI_ESCAPE_RE.findall(text):
        if seq == ANSI_RESET:
            active = []
        else:
            active.append(seq)
    return active


def _last_break_position(text: str) -> Tuple[int, int]:
    """Return (string_index, visible_width_before_index) for the last useful break."""
    last_idx = -1
    last_width = 0
    width = 0
    i = 0
    while i < len(text):
        m = ANSI_ESCAPE_RE.match(text, i)
        if m:
            i = m.end()
            continue
        ch = text[i]
        if ch == " ":
            last_idx = i
            last_width = width
        width += terminal_char_width(ch)
        i += 1
    return last_idx, last_width


def ansi_wrap_line(text: str, width: int) -> List[str]:
    """Wrap one ANSI-colored line without counting escape sequences as width.

    It tries to break on spaces/arrows/separators first, then falls back to a
    hard UTF-8 character break. ANSI style codes are carried across wrapped
    lines so colors do not corrupt the terminal.
    """
    text = str(text)
    width = max(8, width)
    if terminal_visible_width(text) <= width:
        return [text]
    lines: List[str] = []
    current = ""
    current_w = 0
    active_codes: List[str] = []
    i = 0
    while i < len(text):
        m = ANSI_ESCAPE_RE.match(text, i)
        if m:
            seq = m.group(0)
            current += seq
            if seq == ANSI_RESET:
                active_codes = []
            else:
                active_codes.append(seq)
            i = m.end()
            continue
        ch = text[i]
        if ch == "\n":
            if active_codes:
                current += ANSI_RESET
            lines.append(current.rstrip())
            current = "".join(active_codes)
            current_w = 0
            i += 1
            continue
        cw = terminal_char_width(ch)
        if current_w + cw > width and current_w > 0:
            break_idx, break_w = _last_break_position(current)
            if break_idx > 0 and break_w >= max(8, int(width * 0.35)):
                head = current[:break_idx].rstrip()
                tail = current[break_idx + 1:].lstrip()
                if active_codes:
                    head += ANSI_RESET
                lines.append(head)
                active_codes = _ansi_active_codes_until(tail) or active_codes
                current = "".join(active_codes) + tail
                current_w = terminal_visible_width(tail)
            else:
                if active_codes:
                    current += ANSI_RESET
                lines.append(current.rstrip())
                current = "".join(active_codes)
                current_w = 0
            if ch == " " and current_w == 0:
                i += 1
            continue
        if current_w == 0 and ch == " ":
            i += 1
            continue
        current += ch
        current_w += cw
        i += 1
    if current or not lines:
        if active_codes:
            current += ANSI_RESET
        lines.append(current.rstrip())
    return lines


def wrap_ansi_text(text: str, width: Optional[int] = None) -> List[str]:
    width = terminal_content_width() if width is None else max(8, width)
    out: List[str] = []
    for line in str(text).split("\n"):
        out.extend(ansi_wrap_line(line, width))
    return out or [""]


def visible_pad(text: str, width: int) -> str:
    return str(text) + " " * max(0, width - terminal_visible_width(str(text)))


def terminal_print(*objects: object, sep: str = " ", end: str = "\n") -> None:
    """Screen-width-safe print for ANSI/UTF-8 terminal art."""
    text = sep.join(str(obj) for obj in objects)
    for line in wrap_ansi_text(text, terminal_content_width()):
        sys.stdout.write(line)
        sys.stdout.write("\n")
    if end and end != "\n":
        sys.stdout.write(end)


def print_dimension_bars(values: Dict[str, float], indent: str = "  ") -> None:
    for dim in TRUTH_DIMS:
        guide = DIMENSION_GUIDE[dim]
        theme = dim_theme(dim)
        value = float(values.get(dim, 0.0))
        short = guide["short"]
        head = color_text("%s %s %s" % (theme["symbol"], short, guide["name"]), fg=theme["fg"], bold=True)
        meter = render_dim_meter(value, dim, width=12)
        value_txt = color_text("%.2f/4" % value, fg=theme["glow"], bold=True)
        role_txt = color_text(guide["contract_role"], fg=theme["glow"], italic=True)
        terminal_print("%s%-24s %s %s" % (indent, head, meter, value_txt))
        terminal_print("%s    %s" % (indent, role_txt))


def domain_color(domain: str) -> Tuple[int, int, int]:
    idx = list(DOMAINS).index(domain) if domain in DOMAINS else 0
    palette = [
        (0, 229, 255), (38, 222, 129), (255, 166, 0), (255, 106, 188),
        (58, 134, 255), (255, 214, 10), (161, 108, 255), (255, 87, 87),
        (190, 140, 90), (120, 185, 255), (255, 46, 138), (0, 245, 212),
        (255, 125, 0), (155, 225, 93), (0, 200, 140), (180, 180, 180),
    ]
    return palette[idx % len(palette)]


def domain_badge(domain: str) -> str:
    fg = domain_color(domain)
    bg = tuple(max(0, min(255, int(c * 0.22))) for c in fg)
    return styled_badge(display_domain(domain).upper(), fg, bg)



def pretty_key_value(label: str, value: str, label_fg: Tuple[int, int, int] = (180, 220, 255), value_fg: Tuple[int, int, int] = (255, 255, 255)) -> None:
    label_text = label.ljust(18)
    available = max(12, terminal_content_width() - terminal_visible_width(label_text) - 1)
    wrapped = plain_wrap(value, available)
    for idx, line in enumerate(wrapped):
        if idx == 0:
            terminal_print("%s %s" % (color_text(label_text, fg=label_fg, bold=True), color_text(line, fg=value_fg)))
        else:
            terminal_print("%s %s" % (" " * terminal_visible_width(label_text), color_text(line, fg=value_fg)))


def colorful_bullet(text: str, fg: Tuple[int, int, int]) -> str:
    return color_text("▸", fg=fg, bold=True) + " " + color_text(text, fg=(245, 245, 245))


def terminal_header(title: str, subtitle: str = "") -> None:
    terminal_rule()
    header = "✦ " + title + " ✦"
    for line in plain_wrap(header, terminal_content_width()):
        terminal_print(color_text(line, fg=(255, 255, 255), bg=(35, 35, 35), bold=True))
    if subtitle:
        for line in plain_wrap(subtitle, terminal_content_width()):
            terminal_print(rainbow_text(line))
    terminal_rule()


def terminal_shorten(value: object, limit: int = 118) -> str:
    text = str(value).replace("\n", " ").strip()
    # Limit by visible width, not Python character count. This prevents wide UTF-8
    # symbols from pushing lines over the terminal edge. Long text is later wrapped
    # by terminal_print; this function only keeps huge fields readable.
    limit = max(10, min(limit, terminal_content_width() * 2))
    if terminal_visible_width(text) <= limit:
        return text
    out = ""
    used = 0
    for ch in text:
        cw = terminal_char_width(ch)
        if used + cw >= limit:
            break
        out += ch
        used += cw
    return out.rstrip() + "…"


def terminal_rule(title: str = "", width: Optional[int] = None) -> None:
    screen = terminal_content_width() if width is None else min(max(30, width), terminal_content_width())
    if title:
        label = "❖ " + title.strip() + " ❖"
        label_w = terminal_visible_width(label) + 2
        if label_w >= screen:
            terminal_print(rainbow_text("═" * screen))
            for line in plain_wrap(label, screen):
                terminal_print(rainbow_text(line))
            terminal_print(rainbow_text("═" * screen))
            return
        fill = max(0, screen - label_w)
        left = "═" * (fill // 2)
        right = "═" * (fill - (fill // 2))
        terminal_print(rainbow_text(left + " " + label + " " + right))
    else:
        terminal_print(rainbow_text("═" * screen))


def sentence_items(text: str) -> List[str]:
    """Divide texto largo de condiciones en viñetas legibles de terminal."""
    parts: List[str] = []
    current = ""
    for chunk in text.split(". "):
        chunk = chunk.strip()
        if not chunk:
            continue
        if not chunk.endswith("."):
            chunk = chunk + "."
        if len(chunk) > 230:
            # Keep very long ecology/climate clauses readable without external wrapping libs.
            words = chunk.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > 170:
                    if line:
                        parts.append(line.rstrip())
                    line = word + " "
                else:
                    line += word + " "
            if line:
                parts.append(line.rstrip())
        else:
            parts.append(chunk)
    return parts


def select_visible_flows(flows: List[EffectFlow], limit: int) -> List[EffectFlow]:
    """Pick diverse, visible flows across domains and trade kinds."""
    if limit <= 0 or not flows:
        return []
    selected: List[EffectFlow] = []
    seen = set()
    # First pass: one high-priority flow per kind/domain.
    for flow in sorted(flows, key=lambda f: (f.truth_stack_priority_0_1, f.activated_effect), reverse=True):
        key = (flow.kind, flow.domain)
        if key in seen:
            continue
        selected.append(flow)
        seen.add(key)
        if len(selected) >= limit:
            return selected
    # Second pass: fill by largest activated effect.
    used_ids = set(id(f) for f in selected)
    for flow in sorted(flows, key=lambda f: f.activated_effect, reverse=True):
        if id(flow) not in used_ids:
            selected.append(flow)
            used_ids.add(id(flow))
        if len(selected) >= limit:
            break
    return selected


def print_dimension_guide_terminal() -> None:
    terminal_header(localized_text("dimension_header"), localized_text("dimension_sub"))
    terminal_print(color_text(localized_label("scale") + ":", fg=(255, 214, 10), bold=True) + " " + color_text(localized_text("scale"), fg=(240, 240, 240)))
    terminal_print(color_text(localized_text("stack_order") + ":", fg=(0, 229, 255), bold=True) + " " + render_truth_stack_badges({dim: 4.0 for dim in TRUTH_DIMS}))
    terminal_print(color_text(localized_text("stack_not_money"), fg=(255, 255, 255), italic=True))
    terminal_print("")
    for dim in TRUTH_DIMS:
        g = DIMENSION_GUIDE[dim]
        theme = dim_theme(dim)
        head = styled_badge("%s %s %s" % (theme["symbol"], g["short"], g["name"]), theme["fg"], theme["bg"])
        terminal_print(head)
        terminal_print("  " + color_text(localized_label("question") + ": ", fg=theme["glow"], bold=True) + color_text(g["question"], fg=(245, 245, 245)))
        terminal_print("  " + color_text(localized_label("contract") + ": ", fg=theme["glow"], bold=True) + color_text(g["contract_role"], fg=(245, 245, 245), italic=True))
        terminal_print("  " + color_text(localized_text("old_form") + ": ", fg=theme["glow"], bold=True) + color_text(g["economic_replacement"], fg=(245, 245, 245)))
        sample = {d: 0.0 for d in TRUTH_DIMS}
        sample[dim] = 4.0
        terminal_print("  " + color_text(localized_label("base5") + ":", fg=theme["glow"], bold=True) + " " + render_truth_stack_badges(sample))
        terminal_print("")



def print_trade_catalog_terminal(limit: int = 0) -> None:
    terminal_header(localized_text("catalog_header"), localized_text("catalog_sub"))
    domains = list(DOMAINS)
    if limit and limit > 0:
        domains = domains[:limit]
    for domain in domains:
        item = TRADE_CATALOG[domain]
        fg = domain_color(domain)
        terminal_print(domain_badge(domain))
        pretty_key_value(localized_label("what"), terminal_shorten(item["trade_object"], 170), label_fg=fg)
        pretty_key_value(localized_label("meant"), terminal_shorten(item["meant_as"], 170), label_fg=fg)
        pretty_key_value(localized_label("products"), terminal_shorten(item["products"], 170), label_fg=fg)
        pretty_key_value(localized_label("workplaces"), terminal_shorten(item["workplaces"], 170), label_fg=fg)
        pretty_key_value(localized_label("services"), terminal_shorten(item["services"], 170), label_fg=fg)
        pretty_key_value(localized_label("ecology"), terminal_shorten(item["ecology"], 170), label_fg=fg)
        pretty_key_value(localized_label("climate"), terminal_shorten(item["climate"], 170), label_fg=fg)
        terminal_print(color_text("  " + "─" * max(4, terminal_content_width() - 8), fg=fg))
    terminal_print("")



def print_visible_trade_contracts(flows: List[EffectFlow], limit: int = 16, detail: bool = False) -> None:
    selected = select_visible_flows(flows, limit)
    terminal_header(localized_text("trades_header"), localized_text("trades_sub"))
    if not selected:
        terminal_print(color_text(localized_text("none_flows"), fg=(255, 120, 120), bold=True))
        terminal_print("")
        return
    terminal_print(color_text(localized_text("old_form") + ":", fg=(255, 106, 188), bold=True) + " " + color_text(localized_text("old_form_text"), fg=(240, 240, 240)))
    terminal_print(color_text(localized_text("new_form") + ":", fg=(0, 229, 255), bold=True) + " " + color_text(localized_text("new_form_text"), fg=(240, 240, 240)))
    terminal_print(color_text(localized_text("display") + ":", fg=(255, 214, 10), bold=True) + " " + color_text(localized_text("display_note"), fg=(240, 240, 240), italic=True))
    terminal_print("")
    for idx, flow in enumerate(selected, 1):
        validity = CONTRACT_VALIDITY_LABELS.get(flow.contract_validity, flow.contract_validity)
        title = "%s %03d  %s  %s" % (localized_text("contract"), idx, display_domain(flow.domain).upper(), validity.upper())
        terminal_rule(title, width=None)
        dom_fg = domain_color(flow.domain)
        terminal_print(domain_badge(flow.domain) + " " + color_text(validity.upper(), fg=dom_fg, bold=True) + " " + color_text("•", fg=(255,255,255)) + " " + color_text(display_kind(flow.kind), fg=(220,220,220), italic=True))
        pretty_key_value(localized_label("contract"), display_kind(flow.kind), label_fg=dom_fg)
        pretty_key_value(localized_text("old_form"), display_legacy(flow.legacy_term_replaced), label_fg=dom_fg)
        pretty_key_value(localized_label("action"), display_action(flow.action), label_fg=dom_fg)
        pretty_key_value(localized_label("from_to"), "%s/%s → %s/%s" % (flow.from_region, flow.from_commune, flow.to_region, flow.to_commune), label_fg=dom_fg)
        pretty_key_value(localized_label("sector"), display_sector(flow.sector), label_fg=dom_fg)
        pretty_key_value(localized_label("effect"), "%.3f" % flow.activated_effect, label_fg=dom_fg, value_fg=(255, 240, 170))
        pretty_key_value(localized_label("causal_chain"), terminal_shorten(flow.causal_link, 170), label_fg=dom_fg)
        pretty_key_value(localized_label("direction"), terminal_shorten(flow.direction_vector, 170), label_fg=dom_fg)
        terminal_print(color_text(localized_label("base5"), fg=(255,255,255), bold=True) + ":  " + render_truth_stack_badges(flow.values))
        pretty_key_value(localized_label("base5"), flow.truth_stack_base5, label_fg=(255, 214, 10), value_fg=(255,255,255))
        pretty_key_value("%s / %s" % (localized_label("score"), localized_label("priority")), "%.3f / %.3f" % (flow.truth_stack_score_0_4, flow.truth_stack_priority_0_1), label_fg=(0, 229, 255), value_fg=(255,255,255))
        pretty_key_value(localized_label("meaning"), terminal_shorten(flow.dimension_meaning, 220), label_fg=(255, 106, 188))
        pretty_key_value(localized_label("what"), terminal_shorten(flow.trade_object, 190), label_fg=(38, 222, 129))
        pretty_key_value(localized_label("meant"), terminal_shorten(flow.meant_as, 190), label_fg=(161, 108, 255))
        terminal_print(color_text(localized_text("detail_heading"), fg=(255,255,255), bold=True, underline=True))
        print_dimension_bars(flow.values, indent="  ")
        if detail:
            pretty_key_value(localized_label("products"), terminal_shorten(flow.product_examples, 210), label_fg=(255, 214, 10))
            pretty_key_value(localized_label("workplaces"), terminal_shorten(flow.workplace_examples, 210), label_fg=(255, 166, 0))
            pretty_key_value(localized_label("services"), terminal_shorten(flow.service_examples, 210), label_fg=(58, 134, 255))
            pretty_key_value(localized_label("ecology"), terminal_shorten(flow.ecological_clause, 210), label_fg=(38, 222, 129))
            pretty_key_value(localized_label("climate"), terminal_shorten(flow.climate_clause, 210), label_fg=(0, 229, 255))
            terminal_print(color_text(localized_text("conditions_heading"), fg=(255,255,255), bold=True, underline=True))
            cond_color_cycle = [(255,87,87), (255,166,0), (255,214,10), (38,222,129), (58,134,255), (161,108,255), (255,46,138), (0,229,255)]
            for i, cond in enumerate(sentence_items(flow.contract_conditions)[:12]):
                fg = cond_color_cycle[i % len(cond_color_cycle)]
                terminal_print("  " + colorful_bullet(terminal_shorten(cond, 210), fg))
        else:
            pretty_key_value(localized_label("conditions"), terminal_shorten(flow.contract_conditions, 260), label_fg=(255, 106, 188))
        terminal_print(color_text("┄" * max(4, terminal_content_width() - 2), fg=dom_fg))
        terminal_print("")



def print_truth_stack_explanation_terminal() -> None:
    terminal_header(localized_text("stack_header"), localized_text("stack_sub"))
    sample = {"causality": 3.0, "time": 3.0, "intensity": 4.0, "existence": 4.0, "potencies": 3.0, "effects": 4.0, "substance": 2.0, "matter": 3.0, "difference": 4.0, "determination": 3.0, "phenomena": 4.0, "angle_direction": 3.0}
    terminal_print(color_text(localized_text("base5_example") + ":", fg=(255, 214, 10), bold=True) + " " + color_text("334434234343", fg=(255,255,255), bold=True))
    terminal_print(color_text(localized_text("colored_stack") + ":", fg=(0, 229, 255), bold=True) + " " + render_truth_stack_badges(sample))
    terminal_print(color_text(localized_text("dimensional_readout") + ":", fg=(255,255,255), bold=True, underline=True))
    print_dimension_bars(sample, indent="  ")
    terminal_print(color_text(localized_label("meaning") + ":", fg=(255,255,255), bold=True, underline=True))
    for idx, meaning in enumerate(UI_TEXT.get("example_meanings", [])):
        terminal_print("  " + colorful_bullet(str(meaning), dim_theme(TRUTH_DIMS[idx % len(TRUTH_DIMS)])["fg"]))
    terminal_print("")
    terminal_print(color_text(localized_text("importancia") + ":", fg=(255, 106, 188), bold=True) + " " + color_text(localized_text("stack_warning_1"), fg=(245,245,245)))
    terminal_print(color_text(localized_text("stack_warning_2"), fg=(245,245,245), italic=True))
    terminal_print(color_text(localized_text("stack_warning_3"), fg=(245,245,245)))
    terminal_print("")



# ---------------------------------------------------------------------------
# Extreme UTF-8 / ANSI art gallery for visible planetary economy diagrams
# ---------------------------------------------------------------------------


def art_palette() -> List[Tuple[int, int, int]]:
    return [
        (255, 87, 87), (255, 166, 0), (255, 214, 10), (38, 222, 129),
        (0, 245, 212), (58, 134, 255), (161, 108, 255), (255, 46, 138),
        (0, 229, 255), (255, 106, 188), (190, 140, 90), (155, 225, 93),
    ]


def art_color(index: int) -> Tuple[int, int, int]:
    palette = art_palette()
    return palette[index % len(palette)]


def art_dim_line(dim: str, value: float, width: int = 36) -> str:
    theme = dim_theme(dim)
    guide = DIMENSION_GUIDE[dim]
    available = terminal_content_width() - 34
    width = max(4, min(width, available))
    fill = max(0, min(width, int(round((clamp(value, 0.0, 4.0) / 4.0) * width))))
    meter = color_text("█" * fill, fg=theme["fg"], bold=True) + color_text("░" * (width - fill), fg=(70, 70, 70))
    return "%s %s %s %s" % (
        styled_badge("%s%s" % (theme["symbol"], guide["short"]), theme["fg"], theme["bg"]),
        meter,
        color_text("%4.2f" % value, fg=theme["glow"], bold=True),
        color_text(guide["name"], fg=theme["fg"], bold=True),
    )


def art_box_line(text: str, fg: Tuple[int, int, int], width: int = 100) -> str:
    box_width = min(max(30, width), terminal_content_width())
    inner = max(10, box_width - 2)
    wrapped = plain_wrap(str(text), max(8, inner - 2))
    lines: List[str] = []
    for raw in wrapped:
        body = visible_pad(" " + raw, inner - 1) + " "
        lines.append(color_text("┃", fg=fg, bold=True) + color_text(body, fg=(245, 245, 245)) + color_text("┃", fg=fg, bold=True))
    return "\n".join(lines)


def art_panel(title: str, number: int, subtitle: str = "") -> None:
    fg = art_color(number)
    box_width = terminal_content_width()
    inner = max(10, box_width - 2)
    terminal_print("")
    terminal_print(color_text("╔" + "═" * inner + "╗", fg=fg, bold=True))
    title_lines = plain_wrap("  %02d  %s" % (number, title), inner)
    for line in title_lines:
        terminal_print(color_text("║", fg=fg, bold=True) + color_text(visible_pad(line, inner), fg=fg, bold=True) + color_text("║", fg=fg, bold=True))
    if subtitle:
        for line in plain_wrap("  " + subtitle, inner):
            terminal_print(color_text("║", fg=fg, bold=True) + color_text(visible_pad(line, inner), fg=(255, 255, 255), italic=True) + color_text("║", fg=fg, bold=True))
    terminal_print(color_text("╚" + "═" * inner + "╝", fg=fg, bold=True))


def art_ratio_bar(label: str, ratio: float, fg: Tuple[int, int, int], width: int = 50) -> str:
    ratio = clamp(ratio, 0.0, 1.0)
    label_width = min(24, max(10, terminal_content_width() // 3))
    percent_width = 7
    width = max(3, min(width, terminal_content_width() - label_width - percent_width - 3))
    label_clean = str(label)
    if terminal_visible_width(label_clean) > label_width:
        label_clean = plain_wrap(label_clean, label_width)[0]
    fill = int(round(ratio * width))
    return "%s %s %s" % (
        color_text(visible_pad(label_clean, label_width), fg=fg, bold=True),
        color_text("█" * fill, fg=fg, bold=True) + color_text("░" * (width - fill), fg=(72, 72, 72)),
        color_text("%5.1f%%" % (ratio * 100.0), fg=(255, 255, 255), bold=True),
    )


def art_spark(values: List[float], fg: Tuple[int, int, int], width: int = 60) -> str:
    chars = "▁▂▃▄▅▆▇█"
    width = max(6, min(width, terminal_content_width() - 18))
    if not values:
        return ""
    if len(values) > width:
        step = float(len(values)) / float(width)
        sampled = []
        for i in range(width):
            sampled.append(values[int(i * step)])
    else:
        sampled = list(values)
    mn = min(sampled)
    mx = max(sampled)
    span = mx - mn
    out = []
    for value in sampled:
        if span <= 1e-9:
            idx = 3
        else:
            idx = int(round(((value - mn) / span) * (len(chars) - 1)))
        out.append(color_text(chars[max(0, min(len(chars) - 1, idx))], fg=fg, bold=True))
    return "".join(out)


def top_flows_for_art(flows: List[EffectFlow], limit: int = 8) -> List[EffectFlow]:
    return sorted(flows, key=lambda f: (f.truth_stack_priority_0_1, f.activated_effect), reverse=True)[:limit]


def top_truth_for_art(truth_vectors: List[TruthVector], limit: int = 6) -> List[TruthVector]:
    return sorted(truth_vectors, key=lambda tv: tv.priority(), reverse=True)[:limit]


def macro_by_domain(macro_accounts: List[MacroAccountRow]) -> Dict[str, MacroAccountRow]:
    result: Dict[str, MacroAccountRow] = {}
    for row in macro_accounts:
        result[row.domain] = row
    return result


def art_planet_layer_stack(last: GlobalMetrics) -> None:
    art_panel('Capas planetarias en vez de economía nacional', 1, 'límite planetario')
    layers = [
        ("🌍 PLANETA", "límites: clima, agua, suelo, biodiversidad, material", (0, 229, 255), last.mean_boundary_pressure),
        ("▰ PAÍSES / GRANDES REGIONES", "infraestructura, derecho, equilibrio, protección de crisis", (58, 134, 255), last.coordination_quality),
        ("◈ COMUNAS", "vivienda, agua, alimento, cuidados, energía local", (38, 222, 129), last.wellbeing),
        ("✦ GRUPOS", "capacidades: construcción, cuidados, investigación, reparación, ecología", (255, 214, 10), last.macro_capacity),
        ("● PERSONAS INDIVIDUALES", "necesidad, capacidad, libertad, derecho de objeción", (255, 106, 188), last.avg_autonomy),
    ]
    for name, desc, fg, ratio in layers:
        terminal_print(art_ratio_bar(name, clamp(ratio), fg, width=44))
        terminal_print("   " + color_text("╰─ ", fg=fg) + color_text(desc, fg=(245, 245, 245)))
    terminal_print(color_text("        ╰──────────────────────────────────────────────────────────────────────╯", fg=(161,108,255)))
    terminal_print(color_text("        economía = cambio de realidad dentro de límites planetarios", fg=(255,255,255), bold=True))


def art_truth_stack_totem(flow: Optional[EffectFlow]) -> None:
    art_panel('Tótem de apilamiento de verdad', 2, 'regiones')
    values = flow.values if flow is not None else {dim: 3.0 for dim in TRUTH_DIMS}
    stack = truth_stack_base5(values)
    terminal_print(color_text("APILAMIENTO BASE CINCO: ", fg=(255,214,10), bold=True) + render_truth_stack_badges(values))
    terminal_print(color_text("firma numérica: ", fg=(0,229,255), bold=True) + color_text(stack, fg=(255,255,255), bold=True))
    terminal_print("")
    for dim in TRUTH_DIMS:
        terminal_print("      " + art_dim_line(dim, values.get(dim, 0.0), width=32))
    terminal_print(color_text("      │", fg=(255,255,255)))
    terminal_print(color_text("      ▼", fg=(255,255,255), bold=True))
    terminal_print(color_text("  validez contractual + prioridad + condiciones", fg=(255,106,188), bold=True))


def art_causal_pipeline(flow: Optional[EffectFlow]) -> None:
    art_panel('Cadena causal como flujo de efecto', 3, 'comunas')
    fg = (0, 245, 212)
    parts = ["NECESIDAD", "DIFERENCIA", "CAUSA", "POTENCIA", "SUSTANCIA", "ACCIÓN", "EFECTO", "AUDIT"]
    line = ""
    for i, part in enumerate(parts):
        line += styled_badge(part, art_color(i), tuple(int(c * 0.20) for c in art_color(i)))
        if i < len(parts) - 1:
            line += color_text("━━▶", fg=art_color(i + 1), bold=True)
    terminal_print(line)
    if flow is not None:
        terminal_print(art_box_line("Ejemplo: %s" % flow.causal_link, fg, width=110))
        terminal_print(art_box_line("efecto activado: %.3f | dominio: %s | tipo: %s" % (flow.activated_effect, flow.domain, flow.kind), fg, width=110))
    terminal_print(color_text("          ╭──────────── retroalimentación: fenómenos + error de verdad + informes de personas afectadas ────────────╮", fg=(255,106,188)))
    terminal_print(color_text("          ╰──────────────────────────────────────◀──────────────────────────────────────────────────╯", fg=(255,106,188)))


def art_buy_sell_replacement() -> None:
    art_panel('Compra y venta reconstruidas', 4, 'grupos')
    rows = [
        ("COMPRA", "aceptar efecto de necesidad", "need_acceptance", (255, 106, 188)),
        ("VENTA", "contribuir capacidad/tiempo/sustancia", "contribution_offer", (255, 214, 10)),
        ("IMPORTACIÓN", "transferir efecto desde fuera hacia escasez", "planetary_transfer", (0, 229, 255)),
        ("EXPORTACIÓN", "dar excedente a diferencia real", "planetary_transfer", (38, 222, 129)),
    ]
    for old, new, kind, fg in rows:
        terminal_print(styled_badge(old, fg, tuple(int(c*0.22) for c in fg)) + color_text("  ─────╮", fg=fg, bold=True))
        terminal_print(color_text("              ├──▶ ", fg=fg, bold=True) + color_text(new, fg=(255,255,255), bold=True) + "  " + color_text("[%s]" % kind, fg=fg))
        terminal_print(color_text("              ╰──▶ verdad: Ca/T/I/Ex/P/E/S/M/D/De/F/Da", fg=fg))


def art_boundary_dashboard(last: GlobalMetrics) -> None:
    art_panel('Panel de límites planetarios', 5, 'personas')
    # We do not store every boundary in GlobalMetrics, so use visible metrics plus worst boundary.
    proxies = [
        ("climate", last.worst_boundary_pressure if last.worst_boundary == "climate" else min(1.0, last.mean_boundary_pressure * 1.05)),
        ("biosphere", min(1.0, last.mean_boundary_pressure * 0.97 + 0.03)),
        ("freshwater", min(1.0, last.mean_boundary_pressure * 0.93 + 0.04)),
        ("soil", min(1.0, last.mean_boundary_pressure * 0.90 + 0.06)),
        ("pollution", min(1.0, last.mean_boundary_pressure * 0.95 + 0.05)),
        ("material", min(1.0, last.mean_boundary_pressure * 0.88 + 0.02)),
        ("energy", min(1.0, last.mean_boundary_pressure * 0.92 + 0.03)),
    ]
    for i, (name, pressure) in enumerate(proxies):
        fg = art_color(i + 2)
        danger = pressure > 1.0
        label = ("⚠ " if danger else "✓ ") + name
        terminal_print(art_ratio_bar(label, min(pressure, 1.35) / 1.35, fg, width=54) + "  " + color_text("%.3f" % pressure, fg=(255, 255, 255), bold=True))
    terminal_print(color_text("exceso total: %.4f | límite más crítico: %s %.3f" % (last.overshoot, last.worst_boundary, last.worst_boundary_pressure), fg=(255, 87, 87), bold=True))


def art_climate_contract_shield(last: GlobalMetrics) -> None:
    art_panel('Escudo de contrato climático', 6, 'necesidad')
    fg1, fg2, fg3 = (0, 229, 255), (255, 214, 10), (255, 87, 87)
    terminal_print(color_text("                 ╭────────────────────────────╮", fg=fg1, bold=True))
    terminal_print(color_text("             ╭───┤   COMPROBACIÓN DE RELEVANCIA CLIMÁTICA  ├───╮", fg=fg1, bold=True))
    terminal_print(color_text("             │   ╰────────────────────────────╯   │", fg=fg1, bold=True))
    terminal_print(color_text("        CO₂  │   energía  material  transporte     │  calor", fg=fg2, bold=True))
    terminal_print(color_text("             │        ╲      │      ╱             │", fg=fg2, bold=True))
    terminal_print(color_text("             │         ╲     ▼     ╱              │", fg=fg2, bold=True))
    terminal_print(color_text("             │       DIRECCIÓN ANGULAR R             │", fg=fg3, bold=True))
    terminal_print(color_text("             ╰──────────────┬─────────────────────╯", fg=fg1, bold=True))
    terminal_print(color_text("                            ▼", fg=fg1, bold=True))
    terminal_print(color_text("                  contrato: válido / condicional / bloqueado", fg=(255,255,255), bold=True))
    terminal_print(art_ratio_bar("indicador de presión climática", clamp(last.worst_boundary_pressure / 1.4), fg3, width=50))


def art_material_cycle(last: GlobalMetrics) -> None:
    art_panel('Ciclo de sustancia y materia', 7, 'sustancia')
    fg = (38, 222, 129)
    terminal_print(color_text("        ┌──────────────┐      ┌──────────────┐      ┌──────────────┐", fg=fg, bold=True))
    terminal_print(color_text("        │  SUSTANCIA S  │ ───▶ │  PRODUCCIÓN  │ ───▶ │  USO     │", fg=fg, bold=True))
    terminal_print(color_text("        └──────┬───────┘      └──────┬───────┘      └──────┬───────┘", fg=fg, bold=True))
    terminal_print(color_text("               │                     │                     │", fg=fg, bold=True))
    terminal_print(color_text("               ▼                     ▼                     ▼", fg=fg, bold=True))
    terminal_print(color_text("        ┌──────────────┐      ┌──────────────┐      ┌──────────────┐", fg=(255,214,10), bold=True))
    terminal_print(color_text("        │  REPARACIÓN   │ ◀─── │  RESIDUO Δ    │ ◀─── │  DESGASTE │", fg=(255,214,10), bold=True))
    terminal_print(color_text("        └──────────────┘      └──────────────┘      └──────────────┘", fg=(255,214,10), bold=True))
    terminal_print(art_ratio_bar("circularity_index", last.circularity_index, (0,245,212), width=46))
    terminal_print(art_ratio_bar("repair_materials", clamp(last.repair_materials / max(1.0, last.repair_materials + last.waste_stock)), (255,106,188), width=46))


def art_commune_network(flows: List[EffectFlow]) -> None:
    art_panel('Red de efectos comunales', 8, 'efecto')
    selected = top_flows_for_art(flows, 6)
    nodes = ["◉", "◎", "●", "◌", "◍", "◐"]
    for i, flow in enumerate(selected):
        fg = domain_color(flow.domain)
        left = "%s %s/%s" % (nodes[i % len(nodes)], flow.from_region, flow.from_commune)
        right = "%s/%s %s" % (flow.to_region, flow.to_commune, nodes[(i + 2) % len(nodes)])
        arrow = "═" * (8 + (i % 5)) + "▶"
        terminal_print(color_text(left.ljust(34), fg=fg, bold=True) + color_text(arrow, fg=fg, bold=True) + color_text(right, fg=(255,255,255), bold=True))
        terminal_print("    " + domain_badge(flow.domain) + " " + color_text(flow.kind, fg=fg) + " " + color_text("%.2f unidades de efecto" % flow.activated_effect, fg=(255,240,170), bold=True))
    if not selected:
        terminal_print(color_text("No hay flujos disponibles.", fg=(255,87,87), bold=True))


def art_products_jobs_services_map() -> None:
    art_panel('Productos, puestos de trabajo, servicios', 9, 'verdad')
    trio = [
        ("PRODUCTOS", "herramientas • alimento • agua • vivienda • medicina • baterías", (255,214,10)),
        ("PUESTOS DE TRABAJO", "cuidados • reparación • agricultura • investigación • construcción • energía", (255,106,188)),
        ("SERVICIOS", "sanación • educación • transporte • auditoría • distribución • cuidado", (0,229,255)),
        ("ECOLOGÍA", "suelo • balance hídrico • enfriamiento • biodiversidad • hábitat", (38,222,129)),
    ]
    terminal_print(color_text("                 ╭──────────── CONTRATO DE EFECTO ────────────╮", fg=(255,255,255), bold=True))
    for name, desc, fg in trio:
        terminal_print(color_text("    ", fg=fg) + styled_badge(name, fg, tuple(int(c*0.20) for c in fg)) + color_text(" ───▶ ", fg=fg, bold=True) + color_text(desc, fg=(245,245,245)))
    terminal_print(color_text("                 ╰────── verdad + condiciones + auditoría ───╯", fg=(255,255,255), bold=True))


def art_service_constellation() -> None:
    art_panel('Constelación de servicios', 10, 'corrección')
    center = color_text("       ✦ REPRODUCCIÓN ✦", fg=(255,255,255), bg=(50,20,90), bold=True)
    terminal_print(color_text("             health", fg=domain_color("health"), bold=True) + "        " + color_text("care", fg=domain_color("care"), bold=True))
    terminal_print(color_text("                ╲         ╱", fg=(255,106,188), bold=True))
    terminal_print(color_text("                 ╲       ╱", fg=(255,106,188), bold=True))
    terminal_print("                  " + center)
    terminal_print(color_text("                 ╱   │   ╲", fg=(0,229,255), bold=True))
    terminal_print(color_text("        education    │    mobility", fg=(0,229,255), bold=True))
    terminal_print(color_text("                     governance", fg=domain_color("governance"), bold=True))
    terminal_print(color_text("Cada borde es un flujo de efecto: tiempo, confianza, cuidados, conocimiento, acceso.", fg=(245,245,245)))


def art_angle_compass(flow: Optional[EffectFlow]) -> None:
    art_panel('Brújula de dirección angular', 11, 'libertad')
    r = flow.values.get("angle_direction", 3.0) if flow is not None else 3.0
    fg = dim_theme("angle_direction")["fg"]
    terminal_print(color_text("                         ↑ regenerativo / libre", fg=(38,222,129), bold=True))
    terminal_print(color_text("                         │", fg=fg, bold=True))
    terminal_print(color_text("        localmente adecuado ◀──┼──▶ planetariamente adecuado", fg=fg, bold=True))
    terminal_print(color_text("                         │", fg=fg, bold=True))
    terminal_print(color_text("                         ↓ explotador / controlador", fg=(255,87,87), bold=True))
    terminal_print(art_ratio_bar("Da dirección angular", r / 4.0, fg, width=52))
    if flow is not None:
        terminal_print(color_text("Dirección de ejemplo: ", fg=fg, bold=True) + color_text(flow.direction_vector, fg=(245,245,245)))


def art_difference_funnel(flow: Optional[EffectFlow]) -> None:
    art_panel('Embudo de diferencia', 12, 'regeneración')
    d = flow.values.get("difference", 3.0) if flow is not None else 3.0
    fg = dim_theme("difference")["fg"]
    terminal_print(color_text("        necesidad / urgencia / posibilidad", fg=(255,255,255), bold=True))
    terminal_print(color_text("      ╱════════════════════════════╲", fg=fg, bold=True))
    terminal_print(color_text("     ╱   vivienda  alimento  cuidados   ╲", fg=fg, bold=True))
    terminal_print(color_text("    ╱   agua  energía  ecología    ╲", fg=fg, bold=True))
    terminal_print(color_text("    ╲              Δ                 ╱", fg=fg, bold=True))
    terminal_print(color_text("     ╲       diferencia se resuelve          ╱", fg=fg, bold=True))
    terminal_print(color_text("      ╲      contrato de efecto        ╱", fg=fg, bold=True))
    terminal_print(color_text("       ╲═══════════▼═══════════════╱", fg=fg, bold=True))
    terminal_print(color_text("             acción / efecto", fg=(38,222,129), bold=True))
    terminal_print(art_ratio_bar("D diferencia", d / 4.0, fg, width=52))


def art_contract_gate(flow: Optional[EffectFlow]) -> None:
    art_panel('Puerta de contrato de verdad', 13, 'límite planetario')
    validity = flow.contract_validity if flow is not None else "valid"
    score = flow.truth_stack_priority_0_1 if flow is not None else 0.75
    gates = [
        ("EXISTENCIA", "¿El estado es real?", "existence"),
        ("CAUSALIDAD", "¿Toca la causa?", "causality"),
        ("DIFERENCIA", "¿Hay una brecha real?", "difference"),
        ("DIRECCIÓN", "¿Es regenerativo y libre?", "angle_direction"),
        ("DETERMINACIÓN", "¿Está legitimado?", "determination"),
    ]
    for name, question, dim in gates:
        fg = dim_theme(dim)["fg"]
        value = flow.values.get(dim, 3.0) if flow is not None else 3.0
        terminal_print(styled_badge(name, fg, dim_theme(dim)["bg"]) + " " + art_ratio_bar(question, value / 4.0, fg, width=38))
    terminal_print(color_text("    ╰──────▶ resultado: ", fg=(255,255,255), bold=True) + styled_badge(validity.upper(), (255,255,255), (40,70,40)) + color_text("  prioridad %.3f" % score, fg=(255,214,10), bold=True))


def art_no_money_map() -> None:
    art_panel('Mapa del núcleo sin dinero', 14, 'regiones')
    old = ["precio", "valor", "ganancia", "salario", "renta", "producto interno bruto", "poder adquisitivo", "valor de exportación"]
    new = ["causalidad", "efecto", "diferencia", "sustancia", "materia", "determinación", "potencias", "dirección"]
    for i in range(len(old)):
        terminal_print(styled_badge(old[i], (255,87,87), (70,10,10)) + color_text("  ═══════▶  ", fg=art_color(i), bold=True) + styled_badge(new[i], art_color(i), tuple(int(c*0.20) for c in art_color(i))))


def art_macro_accounts(macro_accounts: List[MacroAccountRow]) -> None:
    art_panel('Cuentas planetarias', 15, 'comunas')
    rows = sorted(macro_accounts, key=lambda r: r.priority, reverse=True)[:8]
    for i, row in enumerate(rows):
        fg = domain_color(row.domain)
        terminal_print(domain_badge(row.domain) + " " + color_text(row.sector, fg=(245,245,245), bold=True))
        terminal_print("  " + art_ratio_bar("satisfaction", row.satisfaction, fg, width=36))
        terminal_print("  " + art_ratio_bar("priority", row.priority, art_color(i + 3), width=36))
        terminal_print("  " + art_ratio_bar("boundary penalty", row.boundary_penalty, art_color(i + 5), width=36))


def art_ecology_mandala(last: GlobalMetrics) -> None:
    art_panel('Mandala de regeneración ecológica', 16, 'grupos')
    fg = domain_color("ecology")
    terminal_print(color_text("                  ✺ suelo ✺", fg=(190,140,90), bold=True))
    terminal_print(color_text("             ╭──────┼──────╮", fg=fg, bold=True))
    terminal_print(color_text("        agua ─── 🌍 ─── biodiversidad", fg=fg, bold=True))
    terminal_print(color_text("             ╰──────┼──────╯", fg=fg, bold=True))
    terminal_print(color_text("                  ✺ enfriamiento ✺", fg=(0,229,255), bold=True))
    terminal_print(color_text("        La regeneración baja riesgos y aumenta la capacidad reproductiva.", fg=(245,245,245)))
    terminal_print(art_ratio_bar("reproduction index", last.planetary_reproduction_index, fg, width=54))


def art_storage_time_bridge(last: GlobalMetrics) -> None:
    art_panel('Almacenamiento como puente temporal', 17, 'personas')
    fg = domain_color("storage")
    terminal_print(color_text("    AHORA ────── alimento/agua/energía ──────▶ DESPUÉS", fg=fg, bold=True))
    terminal_print(color_text("          ╲                                   ╱", fg=fg, bold=True))
    terminal_print(color_text("           ╲_______ almacenamiento / reserva ______╱", fg=fg, bold=True))
    terminal_print(art_ratio_bar("basic_buffer_months", clamp(last.basic_buffer_months / 6.0), fg, width=52))
    terminal_print(art_ratio_bar("resilience_index", last.resilience_index, (255,166,0), width=52))


def art_governance_feedback(last: GlobalMetrics) -> None:
    art_panel('Determinación y corrección', 18, 'necesidad')
    fg = domain_color("governance")
    terminal_print(color_text("   personas afectadas ──▶ informe ──▶ valor de verdad ──▶ contrato ──▶ efecto", fg=fg, bold=True))
    terminal_print(color_text("       ▲                                                           │", fg=fg, bold=True))
    terminal_print(color_text("       └──────────── auditoría ◀── comprobación de error ◀── fenómenos ◀──────┘", fg=fg, bold=True))
    terminal_print(art_ratio_bar("coordination_quality", last.coordination_quality, fg, width=52))
    terminal_print(art_ratio_bar("error de verdad invertido", 1.0 - clamp(last.avg_truth_error), (38,222,129), width=52))


def art_truth_dna(flow: Optional[EffectFlow]) -> None:
    art_panel('ADN de verdad', 19, 'sustancia')
    values = flow.values if flow is not None else {dim: 3.0 for dim in TRUTH_DIMS}
    left = []
    right = []
    for i, dim in enumerate(TRUTH_DIMS):
        theme = dim_theme(dim)
        digit = truth_digit(values.get(dim, 0.0))
        guide = DIMENSION_GUIDE[dim]
        left.append(color_text("%s%s%d" % (theme["symbol"], guide["short"], digit), fg=theme["fg"], bold=True))
        right.append(color_text("%d%s%s" % (digit, guide["short"], theme["symbol"]), fg=theme["fg"], bold=True))
    for i in range(len(TRUTH_DIMS)):
        twist = "╲╱" if i % 2 == 0 else "╱╲"
        terminal_print("      %s  %s  %s" % (left[i].ljust(20), color_text(twist, fg=art_color(i), bold=True), right[i]))


def art_domain_rainbow() -> None:
    art_panel('Arco iris de dominios', 20, 'efecto')
    row = ""
    for i, domain in enumerate(DOMAINS):
        row += domain_badge(domain) + " "
        if (i + 1) % 4 == 0:
            terminal_print(row)
            row = ""
    if row:
        terminal_print(row)
    terminal_print(color_text("Todos los dominios comparten las mismas doce dimensiones de verdad, pero distintos productos, puestos de trabajo y requisitos climáticos.", fg=(245,245,245)))


def art_resilience_radar(last: GlobalMetrics) -> None:
    art_panel('Radar de resiliencia', 21, 'verdad')
    metrics = [
        ("reserva de agua", clamp(last.water_stock / max(1.0, last.water_stock + last.population * 0.01)), domain_color("water")),
        ("reserva de alimento", clamp(last.food_stock / max(1.0, last.food_stock + last.population * 0.01)), domain_color("food")),
        ("reserva de energía", clamp(last.energy_stock / max(1.0, last.energy_stock + last.population * 0.01)), domain_color("energy")),
        ("coordinación", last.coordination_quality, domain_color("governance")),
        ("autonomía", last.avg_autonomy, (255,106,188)),
        ("reparación", last.circularity_index, domain_color("repair")),
    ]
    for name, ratio, fg in metrics:
        terminal_print(art_ratio_bar(name, ratio, fg, width=48))


def art_phenomena_wall(truth_vectors: List[TruthVector]) -> None:
    art_panel('Muro de fenómenos', 22, 'corrección')
    selected = top_truth_for_art(truth_vectors, 8)
    for tv in selected:
        fg = domain_color(tv.domain)
        ph = tv.values.get("phenomena", 0.0)
        terminal_print(domain_badge(tv.domain) + " " + color_text("%s/%s" % (tv.region, tv.commune), fg=(245,245,245), bold=True))
        terminal_print("  " + art_ratio_bar("fenómenos", ph / 4.0, dim_theme("phenomena")["fg"], width=44))
        terminal_print("  " + color_text(terminal_shorten(tv.explanation, 120), fg=(220,220,220)))


def art_potency_garden(truth_vectors: List[TruthVector]) -> None:
    art_panel('Jardín de potencias', 23, 'libertad')
    selected = top_truth_for_art(truth_vectors, 10)
    for i, tv in enumerate(selected):
        p = tv.values.get("potencies", 0.0)
        flowers = int(round(p))
        fg = dim_theme("potencies")["fg"]
        terminal_print(color_text(("✿" * flowers).ljust(6), fg=fg, bold=True) + domain_badge(tv.domain) + " " + color_text("P=%.2f" % p, fg=fg, bold=True) + " " + color_text(tv.commune, fg=(245,245,245)))


def art_labor_lattice(macro_accounts: List[MacroAccountRow]) -> None:
    art_panel('Retícula de puestos de trabajo', 24, 'regeneración')
    rows = sorted(macro_accounts, key=lambda r: r.contribution_time, reverse=True)[:10]
    for i, row in enumerate(rows):
        fg = domain_color(row.domain)
        nodes = max(1, min(18, int(round(row.labor_share * 18))))
        terminal_print(domain_badge(row.domain) + " " + color_text("●─" * nodes + "●", fg=fg, bold=True) + " " + color_text("time %.2f" % row.contribution_time, fg=(255,255,255)))


def art_product_wave() -> None:
    art_panel('Olas de producto como portadoras de efecto', 25, 'límite planetario')
    for i, domain in enumerate(["water", "food", "energy", "shelter", "health", "repair", "ecology", "waste"]):
        fg = domain_color(domain)
        products = TRADE_CATALOG[domain]["products"].split(",")[:5]
        wave = color_text("~≈∿≈~", fg=fg, bold=True)
        terminal_print(domain_badge(domain) + " " + wave + " " + color_text(" | ".join(p.strip() for p in products), fg=(245,245,245)) + " " + wave)


def art_effect_ocean(flows: List[EffectFlow]) -> None:
    art_panel('Océano de efectos', 26, 'regiones')
    selected = top_flows_for_art(flows, 12)
    for i, flow in enumerate(selected):
        fg = domain_color(flow.domain)
        height = max(1, min(10, int(round(flow.truth_stack_priority_0_1 * 10))))
        terminal_print(color_text("≋" * (height + 4), fg=fg, bold=True) + " " + domain_badge(flow.domain) + " " + color_text(flow.kind, fg=(245,245,245)) + " " + color_text("%.2f" % flow.activated_effect, fg=(255,240,170), bold=True))


def art_heatmap_dimensions(flows: List[EffectFlow]) -> None:
    art_panel('Mapa térmico contractual', 27, 'comunas')
    selected = top_flows_for_art(flows, 8)
    if not selected:
        terminal_print(color_text("No hay flujos disponibles.", fg=(255,87,87), bold=True))
        return
    terminal_print(color_text("          ", fg=(255,255,255)) + " ".join(color_text("%02d" % (i + 1), fg=domain_color(f.domain), bold=True) for i, f in enumerate(selected)))
    shade = "░▒▓█"
    for dim in TRUTH_DIMS:
        theme = dim_theme(dim)
        guide = DIMENSION_GUIDE[dim]
        row = styled_badge("%s%s" % (theme["symbol"], guide["short"]), theme["fg"], theme["bg"]) + " "
        for flow in selected:
            v = flow.values.get(dim, 0.0)
            idx = max(0, min(len(shade) - 1, int(round((v / 4.0) * (len(shade) - 1)))))
            row += color_text("%s%s" % (shade[idx], shade[idx]), fg=theme["fg"], bold=True) + " "
        terminal_print(row + color_text(guide["name"], fg=theme["fg"], bold=True))


def art_time_river(timeline: List[GlobalMetrics]) -> None:
    art_panel('Flujo temporal de la economía', 28, 'grupos')
    wellbeing = [m.wellbeing for m in timeline]
    unmet = [m.unmet_basic for m in timeline]
    overs = [m.overshoot for m in timeline]
    terminal_print(color_text("wellbeing     ", fg=(38,222,129), bold=True) + art_spark(wellbeing, (38,222,129), width=72))
    terminal_print(color_text("unmet_basic   ", fg=(255,87,87), bold=True) + art_spark(unmet, (255,87,87), width=72))
    terminal_print(color_text("overshoot     ", fg=(255,166,0), bold=True) + art_spark(overs, (255,166,0), width=72))


def art_cyberpunk_manifest() -> None:
    art_panel('Manifiesto de neón', 29, 'personas')
    lines = [
        "MERCANCÍA → FENÓMENO",
        "PRECIO →  APILAMIENTO DE VERDAD",
        "VALOR → EFECTO",
        "CANTIDAD → INTENSIDAD + SUSTANCIA",
        "POSESIÓN → USO + DETERMINACIÓN",
        "GANANCIA → RESOLUCIÓN DE NECESIDAD Y DIFERENCIA",
        "MERCADO → RETROALIMENTACIÓN + AUDITORÍA + COMUNA",
    ]
    for i, line in enumerate(lines):
        terminal_print(rainbow_text("        ░▒▓█  " + line + "  █▓▒░"))


def art_final_sigil() -> None:
    art_panel('Sello final', 30, 'necesidad')
    colors = art_palette()
    sigil = [
        "                 ╭───────────────╮                 ",
        "             ╭───┤  PLANETA 🌍   ├───╮             ",
        "          ╭──┤   ╰──────┬────────╯   ├──╮          ",
        "       ╭──┤  verdad     │   efecto   ├──╮       ",
        "       │  ╰──────┬──────┼──────┬──────╯  │       ",
        "       │         ▼      ▼      ▼         │       ",
        "       │      necesidad  sustancia  dirección │       ",
        "       │         ▲      ▲      ▲         │       ",
        "       ╰─────────┴──────┴──────┴─────────╯       ",
        "              COMUNAS  •  GRUPOS  •  PERSONAS  ",
    ]
    for i, line in enumerate(sigil):
        terminal_print(color_text(line, fg=colors[i % len(colors)], bold=True))




def art_text_lines(number: int, lines: List[str]) -> None:
    for idx, line in enumerate(lines):
        terminal_print(art_box_line(line, art_color(number + idx), width=terminal_content_width()))
    terminal_print("")


def art_metric_rows(number: int, labels: List[str], values: List[float]) -> None:
    for idx, (label, value) in enumerate(zip(labels, values)):
        terminal_print(art_ratio_bar(label, clamp(value, 0.0, 1.0), art_color(number + idx), width=max(18, terminal_content_width() - 24)))
    terminal_print("")


def art_macro_circular_flow(last: GlobalMetrics) -> None:
    art_panel('MACROECONOMÍA: FLUJO CIRCULAR PLANETARIO', 31, 'Vista macro: reproducción, provisión, regeneración y retroalimentación.')
    art_text_lines(31, [
        'necesidad → contribución → efecto → provisión → retroalimentación → nueva necesidad',
        "      ╭───────────────╮      ╭───────────────╮",
        "      │    need      │ ───▶ │ contribution  │",
        "      ╰───────────────╯      ╰───────────────╯",
        "               ▲                       │        ",
        "               │                       ▼        ",
        "      ╭───────────────╮ ◀─── ╭───────────────╮",
        "      │   feedback    │      │    effect     │",
        "      ╰───────────────╯ ───▶ ╰───────────────╯",
        "                    provision / regeneration   ",
        'Los límites planetarios rodean toda la circulación.',
        'Capas de comunas, países y grupos aparecen dentro del flujo de efecto.',
    ])

def art_macro_provision_balance(last: GlobalMetrics) -> None:
    art_panel('MACROECONOMÍA: BALANCE DE PROVISIÓN', 32, 'No es una imagen de precios, sino un estado de necesidad, brecha, regeneración y exceso.')
    art_metric_rows(32, ['bienestar', 'necesidades básicas no cubiertas', 'exceso', 'reproducción planetaria'], [last.wellbeing, 1.0 - last.unmet_basic, 1.0 - clamp(last.overshoot, 0.0, 1.0), last.planetary_reproduction_index])

def art_macro_sector_web() -> None:
    art_panel('MACROECONOMÍA: RED DE SECTORES', 33, 'La macroeconomía como tejido de efectos en vez de cuenta monetaria.')
    art_text_lines(33, [
        'agua ↔ alimentos ↔ energía ↔ vivienda ↔ salud ↔ educación',
        "             water ── food ── energy            ",
        "               ╲        │        ╱              ",
        "                ╲       │       ╱               ",
        "             ecology ─ shelter ─ health         ",
        "                ╱       │       ╲               ",
        "               ╱        │        ╲              ",
        "          repair ── resilience ── education     ",
        'reparación y resiliencia estabilizan todos los dominios.',
        'La ecología no está fuera; es base de producción y vida.',
    ])

def art_macro_domain_matrix() -> None:
    art_panel('MACROECONOMÍA: MATRIZ DE DOMINIOS', 34, 'Cada dominio porta significado de producto, puesto, servicio y clima.')
    art_text_lines(34, [
        "┌──────────────┬─────────┬─────────┬─────────┬─────────┐",
        "│ domain       │ provide │ work    │ service │ ecology │",
        "├──────────────┼─────────┼─────────┼─────────┼─────────┤",
        "│ water        │ ●●●●    │ ●●      │ ●●●     │ ●●●●    │",
        "│ food         │ ●●●●    │ ●●●     │ ●●      │ ●●●     │",
        "│ energy       │ ●●●     │ ●●●     │ ●●      │ ●●      │",
        "│ health       │ ●●●     │ ●●●     │ ●●●●    │ ●●      │",
        "│ repair       │ ●●      │ ●●●●    │ ●●●     │ ●●●     │",
        "└──────────────┴─────────┴─────────┴─────────┴─────────┘",
        'filas = dominios, columnas = provisión, trabajo, servicio, ecología',
        'La coordinación macro significa cerrar brechas reales en muchos campos.',
        'La matriz es colorida porque cada dominio tiene un color de efecto distinto.',
    ])

def art_macro_external_trade() -> None:
    art_panel('MACROECONOMÍA: COMERCIO EXTERIOR PLANETARIO SIN NÚCLEO MONETARIO', 35, 'Transferencia significa movimiento de efecto entre regiones, no arbitraje de precio.')
    art_text_lines(35, [
        'región A ⇄ región B ⇄ región C',
        "   ┌──────────┐     transferencia de efecto      ┌──────────┐",
        "   │ región A │ ═══════════════════════▶ │ región B │",
        "   └──────────┘ ◀═══════════════════════ └──────────┘",
        "          ╲                                      ▲   ",
        "           ╲                                     │   ",
        "            ╲══════▶ región C ◀══════════════════╝   ",
        'El valor de exportación es reemplazado por: diferencia resuelta, ganancia de tiempo y efecto ecológico.',
        'Toda transferencia lleva condiciones contractuales y valores de verdad.',
    ])

def art_macro_control_cockpit(last: GlobalMetrics) -> None:
    art_panel('MACROECONOMÍA: CABINA DE CONTROL', 36, 'La política macro lee error de verdad, autonomía, coordinación y resiliencia.')
    art_metric_rows(36, ['autonomía', 'coordinación', 'resiliencia', 'error de verdad'], [last.avg_autonomy, last.coordination_quality, last.resilience_index, 1.0 - last.avg_truth_error])

def art_macro_regeneration_budget() -> None:
    art_panel('MACROECONOMÍA: PRESUPUESTO DE REGENERACIÓN', 37, 'La fuerza macroeconómica es restauración de la base de vida.')
    art_text_lines(37, [
        'suelo + agua + clima + biodiversidad + reparación + cuidados',
        "      suelo ═══ agua ═══ clima ═══ biodiversidad   ",
        "         ╲        ╲         │         ╱             ",
        "          ╲        ╲        │        ╱              ",
        "             reparación ═══ cuidados ═══ resiliencia         ",
        'Toda inversión se lee como dirección regenerativa o dañina.',
        'La economía más fuerte sana sus propias condiciones.',
    ])

def art_macro_crisis_buffer(last: GlobalMetrics) -> None:
    art_panel('MACROECONOMÍA: AMORTIGUADOR DE CRISIS', 38, 'Tiempo, almacenamiento, conocimiento y confianza son reservas macroeconómicas.')
    art_metric_rows(38, ['lógica de almacenamiento', 'amortiguador de conocimiento', 'reserva de confianza', 'presión de crisis'], [last.resilience_index, 1.0 - last.avg_truth_error, last.avg_autonomy, clamp(last.overshoot, 0.0, 1.0)])

def art_business_operating_cycle() -> None:
    art_panel('ADMINISTRACIÓN DE EMPRESAS: CICLO OPERATIVO DE EFECTO', 39, 'abastecimiento, producción, servicio, mantenimiento, reparación y retorno.')
    art_text_lines(39, [
        'necesidad → planificación → abastecimiento → producción → revisión → entrega → retroalimentación → reparación',
        "necesidad → plan → fuente → producir → probar → entregar → servicio → reparar",
        "  ▲                                                     │       ",
        "  └────────────── retroalimentación y aprendizaje ────────────────┘       ",
        'La organización es un órgano de efecto, no solo una máquina de dinero.',
        'La administración de empresas se vuelve una arquitectura visible de procesos.',
    ])

def art_business_capability_house() -> None:
    art_panel('ADMINISTRACIÓN DE EMPRESAS: CASA DE CAPACIDADES', 40, 'Personas, herramientas, conocimiento, tiempo e infraestructura construyen la casa de la empresa.')
    art_text_lines(40, [
        "                 /\\                                   ",
        "                /  \\                                  ",
        "               /____\\                                 ",
        "              |      |                                 ",
        "              | datos | servicio | producción | cuidados |       ",
        "              |______|_________|_______|______|        ",
        "              | verdad | sustancia | materia | seguridad |  ",
        'techo: propósito y dirección',
        'salas: abastecimiento, fabricación, cuidados, servicio, datos, aprendizaje',
        'fundamento: verdad, determinación, sustancia, materia, seguridad',
    ])

def art_business_process_chain() -> None:
    art_panel('ADMINISTRACIÓN DE EMPRESAS: CADENA DE PROCESOS', 41, 'Del pedido al efecto: cada paso tiene condiciones.')
    art_text_lines(41, [
        'pedido → aclaración de necesidad → revisión causal → planificación del trabajo → ejecución → auditoría → entrega',
        "[pedido]→[aclarar]→[causa]→[plan]→[ejecutar]→[auditoría]→[entregar]",
        "     ╰───────────── retorno de calidad y retroalimentación ─────────────╯  ",
        'La calidad surge mediante retroalimentación, no solo al final.',
        'La cadena es colorida porque cooperan muchos roles profesionales.',
    ])

def art_business_quality_loop() -> None:
    art_panel('ADMINISTRACIÓN DE EMPRESAS: BUCLE DE CALIDAD', 42, 'observar, medir, corregir, volver a probar y liberar.')
    art_text_lines(42, [
        'fenómeno → medición → comparación → corrección → documentación → nueva verdad',
        "observar → medir → comparar → corregir → documentar → liberar",
        "   ▲                                                    │      ",
        "   └──────────────── nueva verdad y nueva revisión ───────────┘      ",
        'La calidad no es un tema lateral, sino verdad contractual en movimiento.',
        'Los bucles evitan que los errores se conviertan en daño.',
    ])

def art_business_inventory_buffers(last: GlobalMetrics) -> None:
    art_panel('ADMINISTRACIÓN DE EMPRESAS: LÓGICA DE INVENTARIO Y AMORTIGUADOR', 43, 'El inventario es puente temporal y escudo de provisión.')
    art_metric_rows(43, ['amortiguador material', 'amortiguador energético', 'amortiguador temporal', 'reserva de reparación'], [last.resilience_index, max(0.0, min(1.0, 0.55 + 0.35 * last.planetary_reproduction_index)), max(0.0, min(1.0, 0.45 + 0.45 * last.coordination_quality)), max(0.0, min(1.0, 0.40 + 0.45 * last.resilience_index))])

def art_business_project_portfolio() -> None:
    art_panel('ADMINISTRACIÓN DE EMPRESAS: PORTAFOLIO DE PROYECTOS', 44, 'Proyectos importantes y urgentes compiten bajo condiciones de verdad.')
    art_text_lines(44, [
        "                    importancia                           ",
        "                     high                               ",
        "            ┌───────────────────────┬──────────────────┐",
        "            │ núcleo regenerativo     │ reparación urgente    │",
        " urgencia    │ and care              │ y protección   │",
        "  high      ├───────────────────────┼──────────────────┤",
        "            │ construcción transformadora  │ reserva posterior    │",
        "            │ and learning          │ y observación  │",
        "            └───────────────────────┴──────────────────┘",
        'cuadrantes: urgente/importante, urgente/después, regenerativo/transformador',
        'La elección de proyectos no sigue solo el rendimiento, sino el efecto y la protección de límites.',
        'La dirección del portafolio se vuelve legible socialmente.',
    ])

def art_business_risk_canvas() -> None:
    art_panel('ADMINISTRACIÓN DE EMPRESAS: LIENZO DE RIESGO', 45, 'Riesgo climático, cadena de suministro, verdad, aceptación, tecnología y salud.')
    art_text_lines(45, [
        "┌──────────────┬──────────────┬──────────────┐",
        f"│ bajo         │ medio        │ alto         │",
        "├──────────────┼──────────────┼──────────────┤",
        f"│ clima        │ bajo         │ medio        │",
        f"│ logística    │ medio        │ alto         │",
        f"│ verdad       │ bajo         │ medio        │",
        f"│ aceptación   │ medio        │ medio        │",
        f"│ tecnología   │ bajo         │ medio        │",
        f"│ salud        │ bajo         │ medio        │",
        "└──────────────┴──────────────┴──────────────┘",
        'Las fuentes de riesgo se vuelven visibles antes de generar daño.',
        'La prudencia gerencial significa ver temprano las condiciones.',
        'Los colores marcan peligro bajo, medio y alto.',
    ])

def art_business_service_blueprint() -> None:
    art_panel('ADMINISTRACIÓN DE EMPRESAS: PLANO DE SERVICIO', 46, 'punto de contacto, informe, procesamiento, efecto y poscuidado.')
    art_text_lines(46, [
        'la persona informa la necesidad → el equipo la registra → el sistema verifica → se activa el efecto → poscuidado',
        "persona → recepción → verificación → activación → cuidados → aprendizaje",
        "   │         │          │             │          │         │   ",
        " informe   contacto   sistema      efecto     servicio  revisión  ",
        'El servicio aparece como cuidado organizado y solución de problemas.',
        'Abajo la cadena vuelve al aprendizaje y a la mejora.',
    ])
def print_utf8_art_gallery_terminal(flows: List[EffectFlow], truth_vectors: List[TruthVector], timeline: List[GlobalMetrics], macro_accounts: List[MacroAccountRow], limit: int = 46) -> None:
    if limit <= 0:
        return
    terminal_header('GALERÍA DE ARTE DE CARACTERES EXTREMADAMENTE COLORIDA', 'Visualizaciones bajo los contratos: diagramas, figuras, ciclos, brújulas, mapas de calor, macroeconomía y administración de empresas.')
    last = timeline[-1]
    top_flow = top_flows_for_art(flows, 1)[0] if flows else None
    panels = [
        lambda: art_planet_layer_stack(last),
        lambda: art_truth_stack_totem(top_flow),
        lambda: art_causal_pipeline(top_flow),
        art_buy_sell_replacement,
        lambda: art_boundary_dashboard(last),
        lambda: art_climate_contract_shield(last),
        lambda: art_material_cycle(last),
        lambda: art_commune_network(flows),
        art_products_jobs_services_map,
        art_service_constellation,
        lambda: art_angle_compass(top_flow),
        lambda: art_difference_funnel(top_flow),
        lambda: art_contract_gate(top_flow),
        art_no_money_map,
        lambda: art_macro_accounts(macro_accounts),
        lambda: art_ecology_mandala(last),
        lambda: art_storage_time_bridge(last),
        lambda: art_governance_feedback(last),
        lambda: art_truth_dna(top_flow),
        art_domain_rainbow,
        lambda: art_resilience_radar(last),
        lambda: art_phenomena_wall(truth_vectors),
        lambda: art_potency_garden(truth_vectors),
        lambda: art_labor_lattice(macro_accounts),
        art_product_wave,
        lambda: art_effect_ocean(flows),
        lambda: art_heatmap_dimensions(flows),
        lambda: art_time_river(timeline),
        art_cyberpunk_manifest,
        art_final_sigil,
        lambda: art_macro_circular_flow(last),
        lambda: art_macro_provision_balance(last),
        art_macro_sector_web,
        art_macro_domain_matrix,
        art_macro_external_trade,
        lambda: art_macro_control_cockpit(last),
        art_macro_regeneration_budget,
        lambda: art_macro_crisis_buffer(last),
        art_business_operating_cycle,
        art_business_capability_house,
        art_business_process_chain,
        art_business_quality_loop,
        lambda: art_business_inventory_buffers(last),
        art_business_project_portfolio,
        art_business_risk_canvas,
        art_business_service_blueprint,
    ]
    for panel in panels[:max(0, min(limit, len(panels)))]:
        panel()
    terminal_print("")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='visualización terminal colorida para economía planetaria de efectos, contratos y dimensiones de verdad', add_help=False)
    parser.add_argument('--ayuda', action="help", help='mostrar esta ayuda y salir')
    parser.add_argument('--pasos', dest="steps", type=int, default=120, help='meses de simulación')
    parser.add_argument('--semilla', dest="seed", type=int, default=42, help='semilla aleatoria')
    parser.add_argument('--población', dest="population", type=float, default=8_100_000_000.0, help='población sintética')
    parser.add_argument('--regiones', dest="regions", type=int, default=12, help='número de biorregiones')
    parser.add_argument('--comunas-por-región', dest="communes_per_region", type=int, default=8, help='comunas por región')
    parser.add_argument('--escenario', dest="scenario", choices=('bienes_comunes_planetarios', 'democracia_local', 'control_tecnocrático', 'crisis_ecológica', 'choque_de_escasez'), default='bienes_comunes_planetarios', help='escenario')
    parser.add_argument('--salida', dest="out", default='salida_planetaria_español', help='directorio de salida')
    parser.add_argument('--silencio', dest="quiet", action="store_true", help='no imprimir resumen final')
    parser.add_argument('--mostrar-comercio', dest="show_trades", type=int, default=16, help='contratos visibles')
    parser.add_argument('--mostrar-detalle', dest="show_trade_detail", action="store_true", help='detalles contractuales completos')
    parser.add_argument('--mostrar-dimensiones', dest="show_dimensions", action="store_true", help='guía de dimensiones')
    parser.add_argument('--mostrar-catálogo', dest="show_catalog", action="store_true", help='catálogo')
    parser.add_argument('--mostrar-explicación-del-apilamiento', dest="show_stack_explanation", action="store_true", help='explicación de apilamiento')
    parser.add_argument('--mostrar-arte', dest="show_art", type=int, default=46, help='cantidad de arte de caracteres')
    parser.add_argument('--forzar-color', dest="force_color", action="store_true", help='forzar color')
    parser.add_argument('--sin-color', dest="no_color", action="store_true", help='desactivar color')
    parser.add_argument('--anchura', dest="width", type=int, default=0, help='forzar anchura terminal')
    return parser.parse_args(argv)

def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    set_forced_terminal_width(getattr(args, "width", 0))
    set_terminal_color_enabled((not args.no_color) and (args.force_color or ((os.environ.get("NO_COLOR") is None) and sys.stdout.isatty())))
    if args.steps < 0:
        raise SystemExit('--pasos debe ser >= 0')
    if args.population <= 0:
        raise SystemExit('--población debe ser > 0')
    if args.regions <= 0 or args.communes_per_region <= 0:
        raise SystemExit('--regiones y --comunas-por-región deben ser > 0')
    internal_scenario = SCENARIO_ARG_TO_INTERNAL.get(args.scenario, args.scenario)
    regions, boundary, planner, timeline, last_truth, macro_accounts, last_flows = run_simulation(seed=args.seed, steps=args.steps, population=args.population, regions_count=args.regions, communes_per_region=args.communes_per_region, scenario=internal_scenario)
    ensure_dir(args.out)
    write_timeline(os.path.join(args.out, localized_file("timeline")), timeline)
    write_communes(os.path.join(args.out, localized_file("communes")), regions)
    write_truth_audit(os.path.join(args.out, localized_file("truth")), last_truth, args.steps)
    write_macro_accounts(os.path.join(args.out, localized_file("macro")), macro_accounts)
    write_effect_flows(os.path.join(args.out, localized_file("flows")), last_flows)
    write_dimension_guide(os.path.join(args.out, localized_file("dimension")))
    write_trade_dimension_catalog(os.path.join(args.out, localized_file("catalog")))
    write_trade_contracts_report(os.path.join(args.out, localized_file("report")), last_flows, last_truth, timeline)
    write_summary(os.path.join(args.out, localized_file("summary")), regions, boundary, planner, timeline, display_scenario(internal_scenario), args.seed)
    write_manifest(os.path.join(args.out, localized_file("manifest")), timeline, boundary, display_scenario(internal_scenario))
    if not args.quiet:
        first = timeline[0]
        last = timeline[-1]
        terminal_header(localized_text("simulation_header"), localized_text("simulation_sub"))
        pretty_key_value(localized_label("scenario"), display_scenario(internal_scenario), label_fg=(255, 106, 188))
        pretty_key_value(localized_label("steps"), str(args.steps), label_fg=(255, 214, 10))
        pretty_key_value(localized_label("regions"), "%s | %s: %s" % (args.regions, localized_label("communes"), args.regions * args.communes_per_region), label_fg=(0, 229, 255))
        pretty_key_value(localized_label("population"), "%s -> %s" % (format_big(first.population), format_big(last.population)), label_fg=(38, 222, 129))
        pretty_key_value(localized_label("wellbeing"), "%.4f -> %.4f (Δ %.4f)" % (first.wellbeing, last.wellbeing, last.wellbeing - first.wellbeing), label_fg=(161, 108, 255))
        pretty_key_value(localized_label("unmet"), "%.4f -> %.4f (Δ %.4f)" % (first.unmet_basic, last.unmet_basic, last.unmet_basic - first.unmet_basic), label_fg=(255, 87, 87))
        pretty_key_value(localized_label("overshoot"), "%.4f -> %.4f (Δ %.4f)" % (first.overshoot, last.overshoot, last.overshoot - first.overshoot), label_fg=(255, 166, 0))
        pretty_key_value(localized_label("truth_error"), "%.4f -> %.4f (Δ %.4f)" % (first.avg_truth_error, last.avg_truth_error, last.avg_truth_error - first.avg_truth_error), label_fg=(255, 46, 138))
        pretty_key_value(localized_label("autonomy"), "%.4f -> %.4f (Δ %.4f)" % (first.avg_autonomy, last.avg_autonomy, last.avg_autonomy - first.avg_autonomy), label_fg=(58, 134, 255))
        pretty_key_value(localized_label("reproduction"), "%.4f -> %.4f (Δ %.4f)" % (first.planetary_reproduction_index, last.planetary_reproduction_index, last.planetary_reproduction_index - first.planetary_reproduction_index), label_fg=(0, 245, 212))
        pretty_key_value(localized_label("resilience"), "%.4f -> %.4f (Δ %.4f)" % (first.resilience_index, last.resilience_index, last.resilience_index - first.resilience_index), label_fg=(190, 140, 90))
        pretty_key_value(localized_label("coordination"), "%.4f -> %.4f (Δ %.4f)" % (first.coordination_quality, last.coordination_quality, last.coordination_quality - first.coordination_quality), label_fg=(255, 106, 188))
        pretty_key_value(localized_label("inequality"), "%.4f -> %.4f (Δ %.4f)" % (first.satisfaction_inequality, last.satisfaction_inequality, last.satisfaction_inequality - first.satisfaction_inequality), label_fg=(120, 185, 255))
        pretty_key_value(localized_label("worst_boundary"), "%s = %.3f" % (display_boundary(last.worst_boundary), last.worst_boundary_pressure), label_fg=(255, 87, 87))
        pretty_key_value(localized_label("outputs"), os.path.abspath(args.out), label_fg=(200, 200, 200))
        terminal_print("")
        if args.show_dimensions:
            print_dimension_guide_terminal()
        if args.show_catalog:
            print_trade_catalog_terminal()
        if args.show_stack_explanation:
            print_truth_stack_explanation_terminal()
        if args.show_trades > 0:
            print_visible_trade_contracts(last_flows, limit=args.show_trades, detail=args.show_trade_detail)
        if args.show_art > 0:
            print_utf8_art_gallery_terminal(flows=last_flows, truth_vectors=last_truth, timeline=timeline, macro_accounts=macro_accounts, limit=args.show_art)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
