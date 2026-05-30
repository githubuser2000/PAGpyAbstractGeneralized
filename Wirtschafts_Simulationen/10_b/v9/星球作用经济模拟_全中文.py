#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
from __future__ import annotations
'星球作用经济模拟\n\n兼容 PyPy3 的完整星球经济模拟，基于堆叠逻辑真值。经济协调因果、时间、强度、存在、潜能、作用、实质、物质、差异、决定、现象和角向，而不是价格、数量、价值和物品交换。'

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
    "time",               # urgency in time
    "intensity",          # strength/severity of the phenomenon
    "existence",          # how real/present the phenomenon is
    "potencies",          # how much solvable possibility exists
    "effects",            # expected positive systemic effect if solved
    "substance",          # input/substance availability
    "matter",             # material/infrastructure proximity
    "difference",         # gap between need and state
    "determination",      # democratically confirmed 优先级 / social determination
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

# 星球ary pressure names. Pressure > 1 means overshoot beyond safe operating space.
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
DIMENSION_GUIDE = {'causality': {'name': '因果',
               'short': '因',
               'question': '行动触及真实原因，还是只触及表面症状？',
               'contract_role': '规定因果证明、试行状态和纠错义务。',
               'economic_replacement': '用因果证明取代价格信号'},
 'time': {'name': '时间',
          'short': '时',
          'question': '作用有多急，必须在哪个时间窗到达？',
          'contract_role': '规定期限、应急通道、持续期和优先级。',
          'economic_replacement': '用真实急迫性取代交付日期'},
 'intensity': {'name': '强度',
               'short': '强',
               'question': '需要、损害、负担或正向作用有多强？',
               'contract_role': '规定投入强度、劳动时间、保护等级和升级。',
               'economic_replacement': '用现象强度取代支付意愿'},
 'existence': {'name': '存在',
               'short': '存',
               'question': '现象是否已经存在、被测量、被报告并可复核？',
               'contract_role': '规定契约基于现实还是基于假设。',
               'economic_replacement': '用状态存在证明取代所有权证明'},
 'potencies': {'name': '潜能',
               'short': '潜',
               'question': '有哪些能力、储备、工具和可能路径？',
               'contract_role': '规定作用可以立即发生、部分发生，还是先建设能力。',
               'economic_replacement': '用真实转化能力取代资本回报'},
 'effects': {'name': '作用',
             'short': '作',
             'question': '会产生哪些正向和负向系统后果？',
             'contract_role': '规定目标作用、副作用审查和责任。',
             'economic_replacement': '用对人、自然和基础设施的真实作用取代利润'},
 'substance': {'name': '实质',
               'short': '实',
               'question': '有哪些物料、能源、食物、水、知识或照护时间可用？',
               'contract_role': '规定物料放行、实质限制和循环义务。',
               'economic_replacement': '用物质条件取代商品价值'},
 'matter': {'name': '物质',
            'short': '物',
            'question': '物质场所和基础设施在哪里，是否可达？',
            'contract_role': '规定地点、物流、邻近性、运输负担和地方可行性。',
            'economic_replacement': '用真实物质位置取代市场进入'},
 'difference': {'name': '差异',
                'short': '差',
                'question': '需要与现有现实之间的缺口有多大？',
                'contract_role': '规定是否行动，以及化解多少矛盾。',
                'economic_replacement': '用需要缺口取代需求'},
 'determination': {'name': '决定',
                   'short': '决',
                   'question': '行动是否经过社会决定、可异议并有意义？',
                   'contract_role': '规定正当性、参与、异议权和责任。',
                   'economic_replacement': '用集体决定取代契约方权力'},
 'phenomena': {'name': '现象',
               'short': '象',
               'question': '状态如何在观察、测量和受影响者报告中显现？',
               'contract_role': '规定证据基础、观察、审计和纠错义务。',
               'economic_replacement': '用显现和反馈逻辑取代市场观察'},
 'angle_direction': {'name': '角向',
                     'short': '向',
                     'question': '行动朝向哪里：再生、中性、剥削还是控制？',
                     'contract_role': '规定行动被允许、附条件、重建或阻断。',
                     'economic_replacement': '用作用方向取代增长方向'}}

TRADE_CATALOG = {'water': {'display_name': '水',
           'trade_object': '水作用：饮水、清洁、管线、储存、水源保护',
           'meant_as': '保障口渴、卫生、健康、农业以及火灾或危机防护',
           'products': '饮水、滤器、水泵、管件、水箱、测量传感器、净化单元',
           'workplaces': '水务技师；水文学者；管线建设者；实验室检测者；应急供水队；水源守护者',
           'services': '净化、漏损寻找、应急分配、质量检测、水井和管线维护',
           'ecology': '水源汇集区不得被抽空；复育和漏损减少是约束条款',
           'climate': '干旱、暴雨和抽水能耗被计入；高耗能方案需要可再生覆盖'},
 'food': {'display_name': '食物',
          'trade_object': '食物作用：热量、营养、土壤肥力、种子、收获时间',
          'meant_as': '身体再生产、健康、地方食物安全和文化适配供给',
          'products': '谷物、蔬菜、豆类、水果、种子、冷却箱、储藏箱、厨房设备',
          'workplaces': '农人；种子守护者；食物加工者；公共厨房；农业生态队',
          'services': '种植计划、收获、加工、储存、分配、公共餐食、营养指导',
          'ecology': '土壤建设、用水、生物多样性和毒害负担是约束条件',
          'climate': '甲烷、肥料、运输、冷却和气候韧性种植塑造角向'},
 'energy': {'display_name': '能源',
            'trade_object': '能源作用：光、热、驱动、电网稳定、储能电量',
            'meant_as': '供给、通信、生产、照护、流动和灾害防护的条件',
            'products': '电、热、太阳能板、风能部件、电池、热泵、线路、控制装置',
            'workplaces': '电工；电网规划者；储能维护者；太阳能和风能安装者；能源合作社；负荷管理者',
            'services': '发电、分配、移峰、修复、保温指导、应急电力优先',
            'ecology': '采矿、占地、拆解和回收属于契约内部',
            'climate': '化石占比、效率、可再生性和排放作用决定许可和优先级'},
 'shelter': {'display_name': '居所',
             'trade_object': '居所作用：保护、空间、温暖、安全、靠近供给',
             'meant_as': '稳定生存基础，而不是用租金或所有权排除',
             'products': '居住空间、保温材料、修复件、卫生设施、模块部件、公共房间',
             'workplaces': '建造者；翻修者；建筑师；空置测绘者；楼宇技师；居住调解者',
             'services': '按需分配、维护、改造、无障碍、节能翻修、邻里照护',
             'ecology': '改造优先于新建；土地封闭、材料循环和地方绿化是条款',
             'climate': '采暖能耗、保温、热防护和隐含排放决定角向'},
 'health': {'display_name': '健康',
            'trade_object': '疗愈作用：诊断、治疗、预防、药物、护理时间',
            'meant_as': '按急迫性而非支付能力稳定身体和心理',
            'products': '药物、敷料、诊断设备、床位、康复辅助、卫生设备',
            'workplaces': '医生；护士；实验室；救援队；治疗师；预防工作者；医疗技师',
            'services': '诊断、治疗、急救、预防、治疗服务、康复、健康教育',
            'ecology': '医疗废物、水和能耗、毒害路径必须闭合',
            'climate': '高温、新疾病负担、应急韧性和抗气候基础设施进入时间和强度'},
 'care': {'display_name': '照护',
          'trade_object': '照护作用：护理、陪伴、保护、时间、关系、减负',
          'meant_as': '维护尊严、日常生活、依赖安全和社会联结',
          'products': '照护辅助、轮椅、床、卫生用品、辅助装置、无障碍设备',
          'workplaces': '照护者；助理；社会工作者；家庭减负队；失智陪伴者；邻里队',
          'services': '基础照护、陪伴、儿童照护、长者照护、残障协助、减负服务',
          'ecology': '短路程和低物料照护优先；废物和卫生必须安全',
          'climate': '脆弱人群的高温和危机准备属于照护契约'},
 'education': {'display_name': '教育',
               'trade_object': '教育作用：能力、判断、知识、自主、未来潜力',
               'meant_as': '发展潜能，而不是只为市场用途训练',
               'products': '学习空间、书籍、设备、工坊、开放课程、学习材料、数字接入',
               'workplaces': '教师；导师；工坊带领者；教育协调者；语言和融合工作者',
               'services': '课程、成人学习、再训练、公民教育、开放实验室',
               'ecology': '生态知识、修复能力和实质循环是教学内容',
               'climate': '气候能力、适应知识和学习基础设施能耗被追踪'},
 'mobility': {'display_name': '流动',
              'trade_object': '移动作用：可达性、运输、邻近、救援路径、货物流',
              'meant_as': '真实需要的可达，而不是出售公里或票价',
              'products': '自行车、公交、列车、充电点、道路、备件、物流软件、救援车辆',
              'workplaces': '驾驶者；线路规划者；自行车和铁路修理者；物流者；无障碍服务者；救援运输者',
              'services': '公共交通、货物流动、应急运输、上学路线、照护出行、共享供给链',
              'ecology': '占地、噪声、空气污染和栖息地切割是契约条件',
              'climate': '每一移动作用的排放、电气化和避免无必要路线决定方向'},
 'manufacturing': {'display_name': '制造',
                   'trade_object': '制造作用：工具、备件、机器能力、修复基础',
                   'meant_as': '无利润压力和人为淘汰的物质转化能力',
                   'products': '工具、备件、机器模块、外壳、水泵、医疗部件、农具',
                   'workplaces': '机器建造者；制作者；开放工坊；质量检测者；物料规划者；循环设计者',
                   'services': '制造、改造、定规、工具借用、开放生产计划、质量控制',
                   'ecology': '新物料居次；可修复性、回收和无毒性为要求',
                   'climate': '能耗强度、工艺热、路径和物料吞吐限制放行'},
 'storage': {'display_name': '储备',
             'trade_object': '储备作用：缓冲、耐久、电网储备、应急库存、时间桥',
             'meant_as': '防护波动、冲击以及需要与生产的时间错位',
             'products': '食物库、水箱、电池、热储、冷链、备件仓',
             'workplaces': '储备协调者；储能技师；库存检测者；冷链维护者；应急物流者',
             'services': '入库、保质检查、储备管理、电网缓冲、危机优先',
             'ecology': '腐败、制冷剂、储备空间和物料使用是实质与物质条件',
             'climate': '储备减少浪费但会使用能源和物料；两者进入方向'},
 'governance': {'display_name': '治理',
                'trade_object': '决定作用：决策、法、冲突解决、权利、真值纠错',
                'meant_as': '星球经济的正当性和错误修正，而不是市场或国家自动统治',
                'products': '规则、记录、决定登记、隐私工具、审计报告、冲突程序',
                'workplaces': '主持者；法律工作者；隐私守护者；公民会议；调解者；审计者；申诉办公室',
                'services': '参与、异议程序、真值复核、资源放行、冲突解决',
                'ecology': '生态边界被公共监督，不能被投票取消',
                'climate': '气候契约需要透明、长时段和抵抗迁移或技术统治的权利'},
 'knowledge': {'display_name': '知识',
               'trade_object': '知识作用：研究、开放计划、诊断、模拟、学习曲线',
               'meant_as': '提高潜能并降低真值错误',
               'products': '开放计划、测量数据、模型、教学材料、建造指南、诊断规程',
               'workplaces': '研究者；数据守护者；模拟工作者；图书馆员；技术转移者；地方学习工坊',
               'services': '分析、建议、开发、记录、知识转移、错误复核',
               'ecology': '知识必须揭示实质后果，不能隐藏外部化',
               'climate': '气候模型、适应知识和技术评估是核心内容'},
 'resilience': {'display_name': '韧性',
                'trade_object': '韧性作用：冗余、应急能力、危机保护、替代路径',
                'meant_as': '防护冲击、气候事件、供给失效和社会断裂',
                'products': '应急储备、无线网络、移动滤水器、备用电力、庇护所、疏散计划',
                'workplaces': '灾害防护者；医疗援助者；电网冗余者；风险分析者；社区演练者；应急物流者',
                'services': '危机计划、演练、应急供给、冗余建设、风险监测、恢复协调',
                'ecology': '韧性不得把自然当牺牲储备；自然缓冲本身是防护基础设施',
                'climate': '高温、洪水、干旱和歉收提高时间与强度，并允许更快再分配'},
 'repair': {'display_name': '修复',
            'trade_object': '修复作用：寿命、再用、备件回收、能力保持',
            'meant_as': '化解物质差异，而不是新买和丢弃',
            'products': '备件、翻新装置、修复衣物、建筑部件、工具组、回收材料',
            'workplaces': '修复工坊；循环设计者；分拣者；维护者；电子、纺织和建筑修复者',
            'services': '修复、维护、诊断、翻新、材料回收、寿命延长',
            'ecology': '减少废物、原料压力和毒害；毒害安全仍为条件',
            'climate': '降低隐含排放和物料吞吐；高耗能修复必须生态上合算'},
 'ecology': {'display_name': '生态',
             'trade_object': '再生作用：土壤、生物多样性、水量平衡、降温、栖息地',
             'meant_as': '星球生命基础作为主动经济工作，而不是免费背景',
             'products': '复育土地、种子、湿地、农林复合、城市绿地、护土材料',
             'workplaces': '生态学者；复育队；森林和农林守护者；水道照护者；生物多样性监测者',
             'services': '土壤建设、再湿化、造林、物种监测、水道复育、降温区域规划',
             'ecology': '这是直接生态基础功能；剥削不得记作再生',
             'climate': '固碳、降温、蓄水和适应提高角向和作用'},
 'waste': {'display_name': '废物',
           'trade_object': '废物差异化解：分拣、毒害封存、回流、堆肥',
           'meant_as': '废物不是副产物，而是可见的未解物质差异',
           'products': '二次材料、堆肥、分拣金属、塑料、安全填埋单元、修复材料',
           'workplaces': '分拣者；回收者；毒害检测者；堆肥者；循环物流者；物料审计者',
           'services': '收集、分离、去污、回收、再用、安全最终储存',
           'ecology': '毒害必须远离土壤、水和身体；先循环后填埋',
           'climate': '甲烷、焚烧、运输和避免新生产决定气候作用'}}

CONTRACT_VALIDITY_LABELS = {'valid': '有效', 'conditional': '附条件有效', 'experimental': '试验性', 'blocked': '阻断并重建'}
DISPLAY_DOMAIN_NAMES = {'water': '水',
 'food': '食物',
 'energy': '能源',
 'shelter': '居所',
 'health': '健康',
 'care': '照护',
 'education': '教育',
 'mobility': '流动',
 'manufacturing': '制造',
 'storage': '储备',
 'governance': '治理',
 'knowledge': '知识',
 'resilience': '韧性',
 'repair': '修复',
 'ecology': '生态',
 'waste': '废物'}
DISPLAY_SECTOR_NAMES = {'primary_reproduction': '初级再生产',
 'infrastructure_energy': '能源基础设施',
 'social_infrastructure': '社会基础设施',
 'care_reproduction': '照护再生产',
 'knowledge_reproduction': '知识再生产',
 'logistics_circulation': '物流循环',
 'material_transformation': '物质转化',
 'resilience_capital': '韧性能力',
 'institutional_coordination': '制度协调',
 'risk_protection': '风险保护',
 'circular_industry': '循环产业',
 'planetary_regeneration': '星球再生',
 'material_difference_resolution': '物质差异化解'}
DISPLAY_BOUNDARY_NAMES = {'climate': '气候',
 'biosphere': '生物圈',
 'freshwater': '淡水',
 'soil': '土壤',
 'pollution': '污染',
 'material_throughput': '物料吞吐',
 'energy_throughput': '能源吞吐'}
SCENARIO_ARG_TO_INTERNAL = {'星球共有': 'planetary_commons',
 '地方民主': 'local_democracy',
 '技术管制': 'technocratic_control',
 '生态危机': 'ecological_crisis',
 '短缺冲击': 'scarcity_shock'}
SCENARIO_INTERNAL_TO_LABEL = {'planetary_commons': '星球共有',
 'local_democracy': '地方民主',
 'technocratic_control': '技术管制',
 'ecological_crisis': '生态危机',
 'scarcity_shock': '短缺冲击'}
SCENARIO_INTERNAL_TO_ARG = {'planetary_commons': '星球共有',
 'local_democracy': '地方民主',
 'technocratic_control': '技术管制',
 'ecological_crisis': '生态危机',
 'scarcity_shock': '短缺冲击'}
DISPLAY_KIND_LABELS = {'need_acceptance': '需要接受',
 'contribution_offer': '贡献提出',
 'planetary_transfer': '作用转移',
 'reserve_building': '储备建设',
 'regeneration_mandate': '再生授权'}
DISPLAY_LEGACY_LABELS = {'buy/consumption': '买入和消耗',
 'sell/labour_supply': '卖出和劳动供给',
 'trade/import/export': '输入和输出',
 'investment/stock_market': '投入和库存市场',
 'environmental_externality': '环境外部性'}
DISPLAY_ACTION_LABELS = {'accept_effect_for_need': '为需要接受作用',
 'activate_causal_effect': '激活因果作用',
 'move_effect_to_difference': '把作用移向差异',
 'build_time_buffer': '建设时间缓冲',
 'restore_planetary_basis': '恢复星球基础'}
UI_LABELS = {'scenario': '方案',
 'steps': '步数',
 'seed': '种子',
 'regions': '区域',
 'communes': '公社',
 'population': '人口',
 'wellbeing': '福祉',
 'unmet': '未满足基础需要',
 'overshoot': '星球越界',
 'truth_error': '真值错误',
 'autonomy': '自主',
 'reproduction': '再生产指数',
 'resilience': '韧性指数',
 'coordination': '协调质量',
 'inequality': '满足不平等',
 'worst_boundary': '最差边界',
 'outputs': '输出',
 'score': '分数',
 '优先级': '优先级',
 'base5': '五进制堆叠',
 'dimensions': '维度',
 'meaning': '含义',
 'what': '交易内容',
 'meant': '意指',
 'products': '产品',
 'workplaces': '工作位置',
 'services': '服务',
 'ecology': '生态条款',
 'climate': '气候条款',
 'conditions': '契约条件',
 'from_to': '来源去向',
 'sector': '部门',
 'effect': '激活作用',
 'causal_chain': '因果链',
 'direction': '角向',
 'validity': '有效性',
 'old_form': '旧形式',
 'new_form': '新形式',
 'display': '显示',
 'art': '统一码图画廊',
 'contract': '契约',
 'question': '问题',
 'action': '行动',
 'scale': '刻度'}
UI_TEXT = {'dimension_header': '交易维度',
 'dimension_sub': '每个真值维度都有自己的颜色、符号和契约角色。',
 'catalog_header': '交易内容',
 'catalog_sub': '产品、工作位置、服务、生态条款和气候条款作为作用被显示。',
 'trades_header': '维度中的可见交易',
 'trades_sub': '极端彩色契约视图：每个维度都有自己的颜色和可见真值条。',
 'stack_header': '堆叠真值',
 'stack_sub': '堆叠是彩色契约和状态签名，不是货币数字。',
 'simulation_header': '星球作用经济模拟',
 'simulation_sub': '用于星球作用经济、契约和真值维度的彩色终端输出',
 'base5_example': '五进制示例',
 'colored_stack': '彩色堆叠',
 'dimensional_readout': '维度读出',
 'importance': '重要',
 'old_form': '旧形式',
 'new_form': '新形式',
 'display': '显示',
 'none_flows': '没有作用流。请增加步数或把交易显示设为大于零。',
 'contract': '契约',
 'detail_heading': '维度细节',
 'conditions_heading': '契约条件',
 'scale': '刻度：0 = 不存在或错误 | 1 = 弱或潜伏 | 2 = 部分 | 3 = 强 | 4 = 关键或高度真实',
 'stack_order': '堆叠顺序',
 'stack_not_money': '堆叠不是货币。它是作用流的契约和状态签名。',
 'old_form_text': '商品 + 数量 + 价格 + 所有权 → 买入/卖出/输入/输出',
 'new_form_text': '因果 + 时间 + 强度 + 存在 + 潜能 + 作用 + 实质 + 物质 + 差异 + 决定 + 现象 + 角向 → 作用契约',
 'display_note': '每一项都是真实作用流，不是货币交易。激活作用是作用单位，不是价值。',
 'stack_warning_1': '堆叠虽以数字保存，但不作为价值或价格使用。',
 'stack_warning_2': '分数排序优先级；单个数字生成契约条件。',
 'stack_warning_3': '高差异而低角向表示：需要真实，但行动必须重建或阻断。',
 'example_meanings': ['因果=3：原因被较好触及。',
                      '时间=3：紧急。',
                      '强度=4：现象非常强。',
                      '存在=4：真实存在，不只是声称。',
                      '潜能=3：解决可能性存在。',
                      '作用=4：高度正向系统作用。',
                      '实质=2：材料、能源或知识只部分可用。',
                      '物质=3：地点和基础设施足够可达。',
                      '差异=4：需要缺口最大可见。',
                      '决定=3：社会和民主决定良好。',
                      '现象=4：强烈可见、被报告或被测量。',
                      '角向=3：行动较为再生和自由。']}
OUTPUT_FILE_NAMES = {'summary': '概要.json',
 'timeline': '时间线.csv',
 'communes': '最终公社.csv',
 'truth': '真值审计.csv',
 'macro': '星球账目.csv',
 'flows': '作用流审计.csv',
 'dimension': '维度指南.csv',
 'catalog': '交易目录.csv',
 'report': '契约报告.md',
 'manifest': '宣言.md'}
UNIT_LABELS = {'billion': '十亿', 'million': '百万', 'thousand': '千'}
LOCAL_FIELD_LABELS = {'step': '步',
 'kind': '种类',
 'legacy_term_replaced': '被取代词',
 'action': '行动',
 'domain': '领域',
 'sector': '部门',
 'trade_object': '交易作用',
 'meant_as': '意指',
 'product_examples': '产品',
 'workplace_examples': '工作位置',
 'service_examples': '服务',
 'ecological_clause': '生态条款',
 'climate_clause': '气候条款',
 'contract_validity': '契约有效性',
 'contract_conditions': '契约条件',
 'truth_stack_score_0_4': '真值堆叠分数零到四',
 'truth_stack_优先级_0_1': '真值堆叠优先级零到一',
 'truth_stack_base5': '五进制真值堆叠',
 'truth_stack_decimal': '真值堆叠十进制',
 'truth_stack_compact': '紧凑真值堆叠',
 'dimension_meaning': '维度含义',
 'from_region': '来源区域',
 'from_commune': '来源公社',
 'to_region': '去向区域',
 'to_commune': '去向公社',
 'activated_effect': '激活作用',
 'causal_link': '因果连接',
 'direction_vector': '方向向量',
 'note': '注释',
 'region': '区域',
 'commune': '公社',
 'biome': '生物区',
 'population': '人口',
 'wellbeing_proxy': '福祉代理',
 'avg_health': '平均健康',
 'avg_education': '平均教育',
 'avg_autonomy': '平均自主',
 'avg_trust': '平均信任',
 'truth_error': '真值错误',
 'democratic_quality': '民主质量',
 'water_stock': '水储量',
 'food_stock': '食物储量',
 'energy_stock': '能源储量',
 'shelter_capacity': '居所能力',
 'health_capacity': '健康能力',
 'care_capacity': '照护能力',
 'education_capacity': '教育能力',
 'mobility_capacity': '流动能力',
 'manufacturing_capacity': '制造能力',
 'storage_capacity': '储存能力',
 'governance_capacity': '治理能力',
 'knowledge_capacity': '知识能力',
 'resilience_capacity': '韧性能力',
 '修复材料': '修复材料',
 'waste': '废弃物',
 'soil_health': '土壤健康',
 'biodiversity': '生物多样性',
 'watershed': '流域',
 'local_pollution': '地方污染',
 'renewable_infrastructure': '可再生基础设施',
 'top_优先级_domain': '最高优先领域',
 'top_优先级': '最高优先级',
 'top_labor_domain': '最高劳动领域',
 'top_labor_share': '最高劳动份额',
 '优先级': '优先级',
 'explanation': '说明',
 'need': '需要',
 'available': '可用',
 'gap': '缺口',
 '满足度': '满足度',
 'labor_share': '劳动份额',
 'contribution_time': '贡献时间',
 'stock_or_capacity': '储量或能力',
 'boundary_penalty': '边界惩罚',
 'activated_flows': '激活流',
 'wellbeing': '福祉',
 'unmet_basic': '未满足基础需要',
 'overshoot': '星球越界',
 'mean_boundary_pressure': '平均边界压力',
 'worst_boundary': '最差边界',
 'worst_boundary_pressure': '最差边界压力',
 'waste_stock': '废弃物储量',
 'global_transfers': '全局转移',
 'contribution_time_per_person': '人均贡献时间',
 '满足度_inequality': '满足不平等',
 '韧性指数': '韧性指数',
 '循环指数': '循环指数',
 'coordination_quality': '协调质量',
 '基础缓冲月数': '基础缓冲月数',
 'macro_capacity': '宏观能力',
 'planetary_reproduction_index': '星球再生产指数',
 'dimension': '维度',
 'name': '名称',
 'short': '缩写',
 'question': '问题',
 'contract_role': '契约角色',
 'economic_replacement': '经济替代',
 'weight': '权重',
 'effects': '作用',
 'potencies': '潜能',
 'substance': '实质',
 'matter': '物质',
 'causality': '因果',
 'time': '时间',
 'intensity': '强度',
 'existence': '存在',
 'difference': '差异',
 'determination': '决定',
 'phenomena': '现象',
 'angle_direction': '角向'}
LOCAL_BIOME_NAMES = {'equatorial_forest': '赤道森林',
 'temperate_mixed': '温带混合区',
 'drylands': '旱地',
 'coastal_delta': '海岸河洲',
 'mountain_water': '山地水区',
 'urban_corridor': '城市走廊',
 'steppe_grainland': '草原粮地',
 'subpolar_periphery': '亚极边缘'}
LOCAL_NOTE_TEXTS = {'contribution time directed by truth-vector 优先级, not wage/price': '贡献时间由真值向量优先级引导，不由工资或价格引导',
 'surplus and deficit matched by urgency, not purchasing power': '盈余和不足按紧急性匹配，不按购买力匹配',
 'need 满足度 accepted through existence/intensity/time, not purchasing power': '需要满足通过存在、强度和时间接受，不通过购买力接受',
 'housing access through real need and capacity, not rent/price': '居住进入依据真实需要和能力，不依据租金或价格',
 'service is used as social effect, not purchased service value': '服务作为社会作用使用，不作为购买服务价值使用'}
LOCAL_DIRECTION_TERMS = {'angle': '角向', 'difference': '差异', 'determination': '决定', 'validity': '有效性'}
LOCAL_SUMMARY_KEYS = {'model': '模型',
 'scenario': '方案',
 'seed': '种子',
 'steps': '步数',
 'regions': '区域',
 'communes': '公社',
 'initial': '初始',
 'final': '最终',
 'delta': '变化',
 'boundary_pressures': '边界压力',
 'planner': '规划器'}
COMMUNE_SUFFIX = '公社'
UNMAPPED_LABEL = '未映射'
NONE_LABEL = '无'

LOCAL_FIELD_LABELS.update({'avg_truth_error': '平均真值错误', 'boundary_penalty': '边界惩罚'})
DISPLAY_LEGACY_LABELS.update({'buy/sell/import/export': '买入、卖出、输入和输出', 'buy/rent': '买入或租用', 'buy/service_purchase': '购买服务'})
DISPLAY_ACTION_LABELS.update({'causal_transfer_to_need': '向需要进行因果转移', 'stabilize_shelter_existence': '稳定居所存在', 'accept_service_effect': '接受服务作用'})
LOCAL_EXPLANATION_FORMAT = '需要缺口=%.3f 潜能=%.3f 信任=%.3f 边界惩罚=%.3f'

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
    if key in ("domain", "top_优先级_domain", "top_labor_domain"):
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
    """Weighted Gini for inequality of 满足度/wellbeing.

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
        return '没有真值'
    sorted_dims = sorted(TRUTH_DIMS, key=lambda d: values.get(d, 0.0), reverse=True)
    strongest = sorted_dims[:3]
    weakest = sorted_dims[-3:]
    strong_txt = ", ".join("%s %.2f" % (DIMENSION_GUIDE[d]["name"], values.get(d, 0.0)) for d in strongest)
    weak_txt = ", ".join("%s %.2f" % (DIMENSION_GUIDE[d]["name"], values.get(d, 0.0)) for d in weakest)
    return "%s: %s; %s: %s" % ('强', strong_txt, '弱或需检查', weak_txt)


def contract_conditions_for_flow(kind: str, domain: str, values: Dict[str, float]) -> Tuple[str, str]:
    if not values:
        return "experimental", '真值缺失；只允许作为观察性试行。'
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
        conditions.append("%s %s" % (n("causality"), '低：首先需要原因调查、试点或地方诊断。'))
    elif causality >= 3.0:
        conditions.append("%s %s" % (n("causality"), '高：作用链可信，可以优先处理。'))
    else:
        conditions.append("%s %s" % (n("causality"), '中：契约包含审计和纠错义务。'))
    if time_v >= 3.0:
        conditions.append("%s %s" % (n("time"), '高：应急或快速路径，短期限，之后复核。'))
    elif time_v < 1.5:
        conditions.append("%s %s" % (n("time"), '低：可以计划，不挤占其他领域的应急空间。'))
    if intensity >= 3.0:
        conditions.append("%s %s" % (n("intensity"), '高：投入强度可以超过通常份额。'))
    if existence < 1.5:
        conditions.append("%s %s" % (n("existence"), '不确定：需要受影响者报告和测量。'))
    if potencies < 1.8:
        conditions.append("%s %s" % (n("potencies"), '不足：先建设能力、工具或群组能力。'))
    if effects >= 3.0:
        conditions.append("%s %s" % (n("effects"), '高：正向系统后果被承认为社会收益。'))
    if substance < 1.8:
        conditions.append("%s %s" % (n("substance"), '不足：限制物料释放，并保障循环或替代来源。'))
    if matter < 1.8:
        conditions.append("%s %s" % (n("matter"), '不利：澄清物流、邻近性或地方基础设施。'))
    if difference >= 3.0:
        conditions.append("%s %s" % (n("difference"), '高：需要与状态之间的真实缺口使行动正当。'))
    elif difference < 1.2 and kind != "contribution_offer":
        conditions.append("%s %s" % (n("difference"), '低：不做优先处理，只做维护或预防。'))
    if determination < 1.8:
        conditions.append("%s %s" % (n("determination"), '弱：需要民主反馈和异议权。'))
    if phenomena < 1.6:
        conditions.append("%s %s" % (n("phenomena"), '弱：改善可见性、报告和审计。'))
    if angle < 1.5:
        conditions.append("%s %s" % (n("angle_direction"), '负向：重新设计行动，防止生态或社会损害。'))
    elif angle >= 3.0:
        conditions.append("%s %s" % (n("angle_direction"), '再生：行动符合星球方向。'))
    else:
        conditions.append("%s %s" % (n("angle_direction"), '有条件：限制副作用和气候作用。'))
    cat = TRADE_CATALOG.get(domain, {})
    if cat.get("ecology"):
        conditions.append("%s: %s" % ('生态条款', cat["ecology"]))
    if cat.get("climate"):
        conditions.append("%s: %s" % ('气候条款', cat["climate"]))
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

    def 优先级(self) -> float:
        """Priority is not price. It is weighted urgency/effect/difference."""
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
            "优先级": round(self.优先级(), 6),
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
    truth_stack_优先级_0_1: float = 0.0
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
            "truth_stack_优先级_0_1": round(self.truth_stack_优先级_0_1, 6),
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
    """星球ary macro-account row without monetary value categories."""

    step: int
    domain: str
    sector: str
    need: float
    available: float
    gap: float
    满足度: float
    优先级: float
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
            "满足度": round(self.满足度, 6),
            "优先级": round(self.优先级, 6),
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
    """星球ary operating space. Values are pressures; >1.0 means overshoot."""

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

    def update_from_满足度(self, 满足度: Dict[str, float], governance_quality: float, privacy_pressure: float) -> None:
        basic = 0.40 * 满足度.get("water", 1.0) + 0.35 * 满足度.get("food", 1.0) + 0.25 * 满足度.get("shelter", 1.0)
        service = 0.45 * 满足度.get("health", 1.0) + 0.25 * 满足度.get("care", 1.0) + 0.20 * 满足度.get("education", 1.0) + 0.10 * 满足度.get("mobility", 1.0)
        civic = 0.34 * 满足度.get("governance", 1.0) + 0.33 * 满足度.get("knowledge", 1.0) + 0.33 * 满足度.get("resilience", 1.0)
        energy = 满足度.get("energy", 1.0)
        # Health moves slowly; severe basic deficits hit it fast.
        health_delta = 0.018 * (basic - 0.78) + 0.010 * (service - 0.75) + 0.006 * (energy - 0.70)
        self.health = clamp(self.health + health_delta, 0.05, 1.0)
        # Education responds to education 满足度, not instantly.
        self.education = clamp(self.education + 0.006 * (满足度.get("education", 1.0) - 0.55) + 0.003 * (满足度.get("knowledge", 1.0) - 0.55), 0.05, 1.0)
        # Autonomy drops under unmet basics and high privacy/control pressure; it rises with civic capability.
        self.autonomy = clamp(self.autonomy + 0.010 * (mean(满足度.values(), 0.9) - 0.72) + 0.006 * (civic - 0.65) - 0.018 * privacy_pressure, 0.05, 1.0)
        # Trust is a local truth-feedback quality. It falls when the system claims truth but fails people.
        self.trust = clamp(self.trust + 0.018 * (mean(满足度.values(), 0.9) - 0.70) + 0.016 * (governance_quality - 0.5) + 0.008 * (civic - 0.65) - 0.012 * privacy_pressure, 0.02, 1.0)
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
    last_满足度: Dict[str, float] = field(default_factory=dict)
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
            repair_gap = normalized_need_gap(max(1.0, pop * 0.18), self.stocks.get("修复材料", 0.0))
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
            return self.stocks.get("修复材料", 0.0)
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
        substance = clamp(0.35 * sat_ratio(self.stocks.get("修复材料", 0.0), max(1.0, pop * 0.05)) +
                          0.25 * sat_ratio(self.stocks.get("energy", 0.0), max(1.0, self.need("energy") * 0.35)) +
                          0.20 * self.environment.get("watershed", 0.7) +
                          0.20 * self.environment.get("soil_health", 0.7))
        matter = clamp(0.55 * (1.0 - self.environment.get("remoteness", 0.5)) + 0.45 * sat_ratio(self.capacities.get("mobility", 0.0), max(1.0, self.need("mobility"))))
        criticality = planner.domain_criticality.get(domain, 0.5)
        time_urgency = clamp(0.45 * gap + 0.40 * criticality + 0.15 * env_penalty)
        intensity = clamp(0.70 * gap + 0.20 * criticality + 0.10 * (1.0 - self.average_health()))
        # Democracy should influence determination, but not allow a majority to erase critical needs.
        collective_claim = clamp(0.55 * gap + 0.25 * self.democratic_quality + 0.20 * self.average_trust())
        # Phenomena combines measured and reported reality; truth_error is noise/uncertainty.
        phenomena = clamp(gap * (1.0 - 0.50 * self.truth_error) + self.average_trust() * 0.15 + self.democratic_quality * 0.10)
        angle = planner.angle_alignment(domain, global_boundary, self)
        values = {
            "causality": scale4(planner.causal_confidence.get(domain, 0.65)),
            "time": scale4(time_urgency),
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

    def update_truth_error(self, avg_满足度: float, planner: "EffectPlanner") -> None:
        # More democratic feedback and trust reduces truth error. High centralization raises it.
        correction = 0.018 * self.democratic_quality * self.average_trust() * planner.democratic_feedback
        failure = 0.014 * max(0.0, 0.68 - avg_满足度)
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
    修复材料: float
    food_stock: float
    water_stock: float
    energy_stock: float
    global_transfers: float
    contribution_time: float
    contribution_time_per_person: float
    满足度_inequality: float
    韧性指数: float
    循环指数: float
    coordination_quality: float
    基础缓冲月数: float
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
            "修复材料": round(self.修复材料, 3),
            "food_stock": round(self.food_stock, 3),
            "water_stock": round(self.water_stock, 3),
            "energy_stock": round(self.energy_stock, 3),
            "global_transfers": round(self.global_transfers, 3),
            "contribution_time": round(self.contribution_time, 3),
            "contribution_time_per_person": round(self.contribution_time_per_person, 6),
            "满足度_inequality": round(self.满足度_inequality, 6),
            "韧性指数": round(self.韧性指数, 6),
            "循环指数": round(self.循环指数, 6),
            "coordination_quality": round(self.coordination_quality, 6),
            "基础缓冲月数": round(self.基础缓冲月数, 6),
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
            reuse = sat_ratio(commune.stocks.get("修复材料", 0.0), max(1.0, commune.population() * 0.10))
            return clamp(0.58 + 0.20 * reuse - 0.12 * max(0.0, material - 1.0))
        if domain == "manufacturing":
            circular = sat_ratio(commune.stocks.get("修复材料", 0.0), max(1.0, commune.population() * 0.18))
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
        优先级 = {tv.domain: tv.优先级() for tv in truth_vectors}
        # 星球ary overshoot boosts ecology/repair/waste and moderates material-heavy sectors.
        overs = boundary.overshoot()
        for domain in ("ecology", "repair", "waste", "resilience", "storage"):
            优先级[domain] = 优先级.get(domain, 0.0) + 0.16 * min(1.0, overs)
        if boundary.pressures.get("material_throughput", 0.0) > 1.0:
            优先级["repair"] = 优先级.get("repair", 0.0) + 0.08
            优先级["manufacturing"] = max(0.0, 优先级.get("manufacturing", 0.0) - 0.05)
        if boundary.pressures.get("climate", 0.0) > 1.0:
            优先级["energy"] = 优先级.get("energy", 0.0) + 0.10 * self.renewable_bias
            优先级["resilience"] = 优先级.get("resilience", 0.0) + 0.06
            优先级["mobility"] = 优先级.get("mobility", 0.0) - 0.04 * boundary.pressures.get("climate", 1.0)
        # Centralization dampens local truth. Democratic feedback amplifies it.
        local_weight = clamp(0.45 + 0.45 * commune.democratic_quality * self.democratic_feedback - 0.25 * self.centralization)
        raw = {}
        for d in DOMAINS:
            raw[d] = max(0.005, base[d] * (1.0 - local_weight) + 优先级.get(d, 0.0) * local_weight)
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

REGION_NAMES = ['北水盆地', '赤道森林带', '河洲共有地', '温带环', '旱地太阳弧', '山地水塔', '草原粮食共有地', '城市修复网', '海岸风带', '亚极储存缘', '岛屿共有地', '高地照护环', '内陆物流网', '雨养农林区', '沙漠边缘聚落', '河城链']

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
        "修复材料": pop * rng.uniform(0.05, 0.22),
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
    优先级_0_1 = safe_div(score_0_4, 4.0)
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
        truth_stack_优先级_0_1=优先级_0_1,
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
            note="contribution time directed by truth-vector 优先级, not wage/price",
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
            repair_used = min(commune.stocks.get("修复材料", 0.0), max(0.0, repair_need))
            commune.stocks["修复材料"] = commune.stocks.get("修复材料", 0.0) - repair_used
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
            repair_material = commune.stocks.get("修复材料", 0.0)
            # First reallocate/repair existing capacity; only then build.
            reuse_bias = clamp(0.55 + 0.35 * planner.sufficiency_norm + 0.25 * shares.get("repair", 0.0))
            material_need = domain_labor * (0.10 + 0.25 * (1.0 - reuse_bias))
            used_mat = min(repair_material, material_need)
            commune.stocks["修复材料"] = repair_material - used_mat
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
            material_used = min(commune.stocks.get("修复材料", 0.0), material_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            commune.stocks["修复材料"] = commune.stocks.get("修复材料", 0.0) - material_used
            input_factor = 0.35 + 0.40 * sat_ratio(energy_used, energy_need) + 0.25 * sat_ratio(material_used, material_need)
            tools = domain_labor * (0.50 + skill) * input_factor
            commune.stocks["修复材料"] = commune.stocks.get("修复材料", 0.0) + 0.42 * tools
            commune.capacities["manufacturing"] = commune.capacities.get("manufacturing", 0.0) + 0.58 * tools
            step_impacts.add_impact("material_throughput", 0.0000000000014 * max(0.0, material_need - material_used) + 0.0000000000005 * material_used)
            step_impacts.add_impact("energy_throughput", 0.00000000000025 * energy_used)
            step_impacts.add_impact("pollution", 0.0000000000007 * max(0.0, tools - material_used))

        elif domain == "storage":
            skill = commune.skill("storage")
            energy_need = 0.035 * domain_labor
            material_need = 0.07 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            material_used = min(commune.stocks.get("修复材料", 0.0), material_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            commune.stocks["修复材料"] = commune.stocks.get("修复材料", 0.0) - material_used
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
            material_used = min(commune.stocks.get("修复材料", 0.0), material_need)
            commune.stocks["修复材料"] = commune.stocks.get("修复材料", 0.0) - material_used
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
            commune.stocks["修复材料"] = commune.stocks.get("修复材料", 0.0) + material_gain
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
            commune.stocks["修复材料"] = commune.stocks.get("修复材料", 0.0) + processed * (0.28 + 0.28 * skill)
            commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) - 0.00000000010 * processed)
            step_impacts.add_regen("pollution", 0.0000000000012 * processed)
            step_impacts.add_regen("material_throughput", 0.0000000000008 * processed)

    # Capacity decay / maintenance burden: if not maintained, infrastructure slowly decays.
    maintenance_quality = clamp(shares.get("repair", 0.0) * 5.0 + shares.get("waste", 0.0) * 2.0 + commune.average_trust() * 0.15)
    decay = 0.0045 * (1.0 - maintenance_quality)
    for cap in MACRO_CAPACITY_DOMAINS:
        commune.capacities[cap] = max(0.0, commune.capacities.get(cap, 0.0) * (1.0 - decay))


def redistribute_planetary_commons(regions: List[Region], planner: EffectPlanner, step_impacts: StepImpacts) -> None:
    """星球ary transfers across regions/communes without prices.

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
                    优先级 = c.last_priorities.get(domain, 0.5)
                    receivers.append([c, deficit, 优先级])
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
            rc, deficit, 优先级 = recv
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
                    note="surplus and deficit matched by urgency, not purchasing power",
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
    满足度: Dict[str, float] = {}
    # Consumables: water, food, energy.
    for domain in CONSUMABLE_DOMAINS:
        need = commune.need(domain)
        stock = commune.stocks.get(domain, 0.0)
        sat = sat_ratio(stock, need)
        used = min(stock, need)
        commune.stocks[domain] = max(0.0, stock - used)
        满足度[domain] = sat
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
                note="need 满足度 accepted through existence/intensity/time, not purchasing power",
            ))

    # Capacities: shelter is not consumed like food; health/care/education/mobility capacity is used this month.
    shelter_need = commune.need("shelter")
    shelter_sat = sat_ratio(commune.capacities.get("shelter", 0.0), shelter_need)
    满足度["shelter"] = shelter_sat
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
        满足度[domain] = sat
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
    consumption_shortfall = 1.0 - mean(满足度.get(d, 1.0) for d in CONSUMABLE_DOMAINS)
    waste_created = pop * 0.028 * (0.65 + 0.35 * mean([满足度.get("food", 1.0), 满足度.get("energy", 1.0)])) * (1.0 - 0.30 * planner.sufficiency_norm)
    # Crisis can create unmanaged waste through breakdown.
    waste_created += pop * 0.012 * consumption_shortfall
    commune.stocks["waste"] = commune.stocks.get("waste", 0.0) + waste_created
    commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) + 0.00000000005 * waste_created)

    # Update cohorts. If system is highly centralized, privacy pressure is stronger.
    privacy = clamp(planner.privacy_pressure + 0.15 * planner.centralization * (1.0 - commune.democratic_quality))
    gov_quality = clamp(0.55 * commune.democratic_quality + 0.30 * commune.average_trust() + 0.15 * (1.0 - commune.truth_error))
    for cohort in commune.cohorts:
        cohort.update_from_满足度(满足度, gov_quality, privacy)

    # Demographic dynamics: cautious and bounded. This is not a detailed population model.
    avg_sat = mean(满足度.values(), 0.85)
    edu = commune.average_education()
    health = commune.average_health()
    # Good conditions sustain; severe unmet basics cause contraction. Higher education moderates growth.
    monthly_growth = 0.00055 * (avg_sat - 0.62) + 0.00035 * (health - 0.55) - 0.00028 * (edu - 0.55)
    monthly_growth = clamp(monthly_growth, -0.0045, 0.0035)
    for cohort in commune.cohorts:
        cohort.size = max(0.0, cohort.size * (1.0 + monthly_growth))

    commune.last_满足度 = 满足度
    commune.update_truth_error(avg_sat, planner)


def simulate_step(regions: List[Region], boundary: BoundaryState, planner: EffectPlanner, step: int) -> Tuple[GlobalMetrics, List[TruthVector], StepImpacts]:
    step_impacts = StepImpacts(step=step)

    # 1) Compute truth vectors: reality -> logical stacked values -> 优先级.
    for region in regions:
        for commune in region.communes:
            tvs = [commune.truth_vector(domain, boundary, planner) for domain in DOMAINS]
            step_impacts.truth_vectors.extend(tvs)
            commune.last_priorities = {tv.domain: tv.优先级() for tv in tvs}
            commune.last_truth_values = {tv.domain: dict(tv.values) for tv in tvs}
            shares = planner.labor_shares(tvs, commune, boundary)
            commune.last_labor_shares = shares

    # 2) Produce local effects according to truth-vector 优先级.
    for region in regions:
        for commune in region.communes:
            produce_local_effects(commune, commune.last_labor_shares, boundary, planner, step_impacts)

    # 3) Redistribute planetary commons: global real need and surplus, no price/currency.
    redistribute_planetary_commons(regions, planner, step_impacts)

    # 4) Consume/satisfy needs and update individuals/cohorts.
    for region in regions:
        for commune in region.communes:
            consume_and_update_people(commune, planner, step_impacts)

    # 5) 星球ary boundary update. Add baseline impacts from unmanaged waste and local pollution.
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
    # Wellbeing from 满足度, health, autonomy, trust, and ecological safety.
    wellbeing_items = []
    unmet_items = []
    basic_buffer_items = []
    resilience_items = []
    for c in communes:
        sat = c.last_满足度 or {d: 0.8 for d in ("water", "food", "energy", "shelter", "health", "care", "education", "mobility", "governance", "knowledge", "resilience")}
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
    修复材料 = sum(c.stocks.get("修复材料", 0.0) for c in communes)
    food_stock = sum(c.stocks.get("food", 0.0) for c in communes)
    water_stock = sum(c.stocks.get("water", 0.0) for c in communes)
    energy_stock = sum(c.stocks.get("energy", 0.0) for c in communes)
    contribution_time = sum(c.productive_time() for c in communes)
    macro_capacity = sum(c.capacities.get(domain, 0.0) for c in communes for domain in MACRO_CAPACITY_DOMAINS)
    avg_truth_error = weighted_mean(((c.truth_error, c.population()) for c in communes), default=0.0)
    avg_democracy = weighted_mean(((c.democratic_quality, c.population()) for c in communes), default=0.0)
    avg_trust = weighted_mean(((c.average_trust(), c.population()) for c in communes), default=0.0)
    循环指数 = clamp(修复材料 / max(1.0, 修复材料 + waste_stock))
    coordination_quality = clamp(0.36 * avg_democracy + 0.34 * avg_trust + 0.30 * (1.0 - avg_truth_error))
    基础缓冲月数 = weighted_mean(basic_buffer_items, default=0.0)
    韧性指数 = weighted_mean(resilience_items, default=0.0)
    满足度_inequality = weighted_gini(wellbeing_items)
    planetary_reproduction_index = clamp(0.30 * weighted_mean(wellbeing_items, default=0.0) +
                                         0.22 * (1.0 - weighted_mean(unmet_items, default=0.0)) +
                                         0.18 * boundary.penalty() +
                                         0.12 * 循环指数 +
                                         0.10 * coordination_quality +
                                         0.08 * 韧性指数)
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
        修复材料=修复材料,
        food_stock=food_stock,
        water_stock=water_stock,
        energy_stock=energy_stock,
        global_transfers=transfers,
        contribution_time=contribution_time,
        contribution_time_per_person=safe_div(contribution_time, total_pop, 0.0),
        满足度_inequality=满足度_inequality,
        韧性指数=韧性指数,
        循环指数=循环指数,
        coordination_quality=coordination_quality,
        基础缓冲月数=基础缓冲月数,
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
        优先级_items = []
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
                stock_or_capacity += c.stocks.get("修复材料", 0.0)
            elif domain == "waste":
                stock_or_capacity += c.stocks.get("waste", 0.0)
            elif domain in MACRO_CAPACITY_DOMAINS:
                stock_or_capacity += c.capacities.get(domain, 0.0)
            优先级_items.append((c.last_priorities.get(domain, 0.0), pop))
            labor_share_items.append((c.last_labor_shares.get(domain, 0.0), pop))
            truth_error_items.append((c.truth_error, pop))
            democracy_items.append((c.democratic_quality, pop))
        gap = normalized_need_gap(need, available)
        满足度 = sat_ratio(available, need)
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
            满足度=满足度,
            优先级=weighted_mean(优先级_items, default=0.0),
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
        "修复材料", "waste",
        "soil_health", "biodiversity", "watershed", "local_pollution", "renewable_infrastructure",
        "top_优先级_domain", "top_优先级", "top_labor_domain", "top_labor_share",
    ]
    rows: List[Dict[str, object]] = []
    for r in regions:
        for c in r.communes:
            sat = c.last_满足度 or {}
            wellbeing_proxy = clamp(0.55 * mean(sat.values(), 0.8) + 0.15 * c.average_health() + 0.15 * c.average_autonomy() + 0.15 * c.average_trust())
            top_优先级 = max(c.last_priorities.items(), key=lambda kv: kv[1]) if c.last_priorities else ("none", 0.0)
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
                "修复材料": round(c.stocks.get("修复材料", 0.0), 3),
                "waste": round(c.stocks.get("waste", 0.0), 3),
                "soil_health": round(c.environment.get("soil_health", 0.0), 6),
                "biodiversity": round(c.environment.get("biodiversity", 0.0), 6),
                "watershed": round(c.environment.get("watershed", 0.0), 6),
                "local_pollution": round(c.environment.get("local_pollution", 0.0), 6),
                "renewable_infrastructure": round(c.environment.get("renewable_infrastructure", 0.0), 6),
                "top_优先级_domain": top_优先级[0],
                "top_优先级": round(top_优先级[1], 6),
                "top_labor_domain": top_labor[0],
                "top_labor_share": round(top_labor[1], 6),
            })
    write_dict_rows_localized(path, rows, fields)


def write_truth_audit(path: str, truth_vectors: List[TruthVector], step: int, limit: int = 500) -> None:
    if not truth_vectors:
        return
    ordered = sorted(truth_vectors, key=lambda tv: tv.优先级(), reverse=True)[:limit]
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
    lines.append('# 维度中的交易：契约、真值堆叠、作用')
    lines.append("")
    lines.append('本协议显示模拟如何取代买入、卖出、输入、输出、劳动市场、产品市场和服务市场。')
    lines.append("")
    lines.append('**旧形式：** 商品 + 数量 + 价格 + 所有权 → 买入/卖出')
    lines.append("")
    lines.append('**新形式：** 因果 + 时间 + 强度 + 存在 + 潜能 + 作用 + 实质 + 物质 + 差异 + 决定 + 现象 + 角向 → 作用契约')
    lines.append("")
    lines.append('堆叠真值是交易的十二维状态。每个维度位于 0..4。五进制堆叠是每个维度一位数字；分数不是货币，而是优先级和有效性数字。')
    lines.append("")
    lines.append('## 维度')
    lines.append("")
    lines.append("| %s | %s | %s | %s |" % ('缩写', '维度', '契约问题', '经济替代'))
    lines.append("|---|---|---|---|")
    for dim in TRUTH_DIMS:
        g = DIMENSION_GUIDE[dim]
        lines.append("| %s | %s | %s | %s |" % (md_escape(g["short"]), md_escape(g["name"]), md_escape(g["question"]), md_escape(g["economic_replacement"])))
    lines.append("")
    lines.append('## 交易内容：产品、工作位置、服务、生态、气候')
    lines.append("")
    lines.append("| %s | %s | %s | %s | %s | %s |" % ('领域', '交易作用', '产品', '工作位置', '服务', '生态和气候条款'))
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
    lines.append('## 最终模拟步的作用契约示例')
    lines.append("")
    lines.append('契约是有条件的作用释放。它说明某个行动可以或应该发生，因为真值堆叠显示真实缺口、原因、时间条件、实质条件、社会决定和角向。')
    lines.append("")
    headers = [localized_label("contract"), localized_label("old_form"), localized_label("domain"), localized_label("what"), localized_label("meant"), localized_label("validity"), localized_label("base5"), localized_label("score"), localized_label("conditions")]
    lines.append("| " + " | ".join(md_escape(h) for h in headers) + " |")
    lines.append("|" + "|".join("---" for _ in headers) + "|")
    for flow in sorted(flows, key=lambda f: (f.truth_stack_优先级_0_1, f.activated_effect), reverse=True)[:limit]:
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
    lines.append('## 堆叠如何关联维度')
    lines.append("")
    for item in ['每个维度测量现实的不同方面：原因、紧急性、强度、存在、可能、后果、材料、地点、缺口、正当性、显现和方向。', '五进制堆叠按照维度顺序保存四舍五入后的数字。', '分数只是排序辅助。单个数字仍然决定契约。', '高差异而低角向表示：需要真实，但行动必须重新设计或阻断。']:
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
        local_field("韧性指数"): getattr(planner, "redistribution_strength", None),
    }
    summary = {
        local_summary_key("model"): '星球作用经济概念模拟',
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
            local_field("韧性指数"): round(last.韧性指数 - first.韧性指数, 6),
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
    lines.append('# 星球经济模拟：扩展作用经济')
    lines.append("")
    lines.append('本模拟不建模以货币、价格、国内总产值、工资、利润、租金或外贸价值为核心的国民经济。')
    lines.append('它建模星球作用经济：需要、材料、潜能、生态边界、时间贡献、能力、部门和社会反馈。')
    lines.append("")
    lines.append('## 核心原则')
    lines.append("")
    lines.append('这里的经济行动不是买入或卖出交易，而是状态改变：')
    lines.append("")
    lines.append("```")
    lines.append('现象 + 因果 + 时间 + 强度 + 存在 + 潜能 + 作用 + 实质 + 物质 + 差异 + 决定 + 现象 + 角向 → 作用契约 → 被改变的现实')
    lines.append("```")
    lines.append("")
    lines.append('## 最终状态')
    lines.append("")
    lines.append("- %s: %s" % ('方案', scenario))
    lines.append("- %s: %.4f → %.4f" % (localized_label("wellbeing"), first.wellbeing, last.wellbeing))
    lines.append("- %s: %.4f → %.4f" % (localized_label("unmet"), first.unmet_basic, last.unmet_basic))
    lines.append("- %s: %.4f → %.4f" % (localized_label("overshoot"), first.overshoot, last.overshoot))
    lines.append("- %s: %.4f → %.4f" % (localized_label("truth_error"), first.avg_truth_error, last.avg_truth_error))
    lines.append("- %s: %.4f → %.4f" % (localized_label("autonomy"), first.avg_autonomy, last.avg_autonomy))
    lines.append("- %s: %s = %.3f" % (localized_label("worst_boundary"), display_boundary(last.worst_boundary), last.worst_boundary_pressure))
    lines.append("")
    lines.append('## 解释')
    lines.append("")
    lines.append('改善意味着更少可避免痛苦、更好的基础需要覆盖、更低越界、更高韧性、更好的真值纠错以及更多真实自主。')
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
    """把较长的契约条件文本切分为适合终端阅读的项目。"""
    parts: List[str] = []
    current = ""
    for chunk in text.split(". "):
        chunk = chunk.strip()
        if not chunk:
            continue
        if not chunk.endswith("."):
            chunk = chunk + "."
        if len(chunk) > 230:
            # 让很长的生态和气候条款在不依赖外部换行库的情况下保持可读。
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
    # First pass: one high-优先级 flow per kind/domain.
    for flow in sorted(flows, key=lambda f: (f.truth_stack_优先级_0_1, f.activated_effect), reverse=True):
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
        pretty_key_value("%s / %s" % (localized_label("score"), localized_label("优先级")), "%.3f / %.3f" % (flow.truth_stack_score_0_4, flow.truth_stack_优先级_0_1), label_fg=(0, 229, 255), value_fg=(255,255,255))
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
    terminal_print(color_text(localized_text("importance") + ":", fg=(255, 106, 188), bold=True) + " " + color_text(localized_text("stack_warning_1"), fg=(245,245,245)))
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
    return sorted(flows, key=lambda f: (f.truth_stack_优先级_0_1, f.activated_effect), reverse=True)[:limit]


def top_truth_for_art(truth_vectors: List[TruthVector], limit: int = 6) -> List[TruthVector]:
    return sorted(truth_vectors, key=lambda tv: tv.优先级(), reverse=True)[:limit]


def macro_by_domain(macro_accounts: List[MacroAccountRow]) -> Dict[str, MacroAccountRow]:
    result: Dict[str, MacroAccountRow] = {}
    for row in macro_accounts:
        result[row.domain] = row
    return result


def art_planet_layer_stack(last: GlobalMetrics) -> None:
    art_panel('星球层级而非国民经济', 1, '星球边界')
    layers = [
        ("🌍 星球", "边界：气候、水、土壤、生物多样性、材料", (0, 229, 255), last.mean_boundary_pressure),
        ("▰ 国家 / 大区域", "基础设施、法律、平衡、危机保护", (58, 134, 255), last.coordination_quality),
        ("◈ 公社", "住房、水、食物、照护、能源在本地", (38, 222, 129), last.wellbeing),
        ("✦ 群组", "能力：建造、照护、研究、修理、生态", (255, 214, 10), last.macro_capacity),
        ("● 个人", "需要、能力、自由、异议权", (255, 106, 188), last.avg_autonomy),
    ]
    for name, desc, fg, ratio in layers:
        terminal_print(art_ratio_bar(name, clamp(ratio), fg, width=44))
        terminal_print("   " + color_text("╰─ ", fg=fg) + color_text(desc, fg=(245, 245, 245)))
    terminal_print(color_text("        ╰──────────────────────────────────────────────────────────────────────╯", fg=(161,108,255)))
    terminal_print(color_text("        经济 = 星球边界内的现实改变", fg=(255,255,255), bold=True))


def art_truth_stack_totem(flow: Optional[EffectFlow]) -> None:
    art_panel('真值堆叠图腾', 2, '区域')
    values = flow.values if flow is not None else {dim: 3.0 for dim in TRUTH_DIMS}
    stack = truth_stack_base5(values)
    terminal_print(color_text("五进制堆叠：", fg=(255,214,10), bold=True) + render_truth_stack_badges(values))
    terminal_print(color_text("数字签名：", fg=(0,229,255), bold=True) + color_text(stack, fg=(255,255,255), bold=True))
    terminal_print("")
    for dim in TRUTH_DIMS:
        terminal_print("      " + art_dim_line(dim, values.get(dim, 0.0), width=32))
    terminal_print(color_text("      │", fg=(255,255,255)))
    terminal_print(color_text("      ▼", fg=(255,255,255), bold=True))
    terminal_print(color_text("  契约有效性 + 优先级 + 条件", fg=(255,106,188), bold=True))


def art_causal_pipeline(flow: Optional[EffectFlow]) -> None:
    art_panel('因果链作为作用流', 3, '公社')
    fg = (0, 245, 212)
    parts = ["需要", "差异", "原因", "潜能", "实质", "行动", "作用", "审计"]
    line = ""
    for i, part in enumerate(parts):
        line += styled_badge(part, art_color(i), tuple(int(c * 0.20) for c in art_color(i)))
        if i < len(parts) - 1:
            line += color_text("━━▶", fg=art_color(i + 1), bold=True)
    terminal_print(line)
    if flow is not None:
        terminal_print(art_box_line("示例：%s" % flow.causal_link, fg, width=110))
        terminal_print(art_box_line("激活作用：%.3f | 领域：%s | 种类：%s" % (flow.activated_effect, flow.domain, flow.kind), fg, width=110))
    terminal_print(color_text("          ╭──────────── 反馈：现象 + 真值错误 + 受影响者报告 ────────────╮", fg=(255,106,188)))
    terminal_print(color_text("          ╰──────────────────────────────────────◀──────────────────────────────────────────────────╯", fg=(255,106,188)))


def art_buy_sell_replacement() -> None:
    art_panel('买入和卖出被重建', 4, '群体')
    rows = [
        ("买入", "接受需要作用", "need_acceptance", (255, 106, 188)),
        ("卖出", "贡献能力/时间/实质", "contribution_offer", (255, 214, 10)),
        ("输入", "把外部作用转移到缺乏处", "planetary_transfer", (0, 229, 255)),
        ("输出", "把盈余给入真实差异", "planetary_transfer", (38, 222, 129)),
    ]
    for old, new, kind, fg in rows:
        terminal_print(styled_badge(old, fg, tuple(int(c*0.22) for c in fg)) + color_text("  ─────╮", fg=fg, bold=True))
        terminal_print(color_text("              ├──▶ ", fg=fg, bold=True) + color_text(new, fg=(255,255,255), bold=True) + "  " + color_text("[%s]" % kind, fg=fg))
        terminal_print(color_text("              ╰──▶ 真值：因/时/强/存/潜/作/实/物/差/决/现/向", fg=fg))


def art_boundary_dashboard(last: GlobalMetrics) -> None:
    art_panel('星球边界面板', 5, '个人')
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
    terminal_print(color_text("总越界：%.4f | 最差边界：%s %.3f" % (last.overshoot, last.worst_boundary, last.worst_boundary_pressure), fg=(255, 87, 87), bold=True))


def art_climate_contract_shield(last: GlobalMetrics) -> None:
    art_panel('气候契约盾', 6, '需要')
    fg1, fg2, fg3 = (0, 229, 255), (255, 214, 10), (255, 87, 87)
    terminal_print(color_text("                 ╭────────────────────────────╮", fg=fg1, bold=True))
    terminal_print(color_text("             ╭───┤   气候相关性检查  ├───╮", fg=fg1, bold=True))
    terminal_print(color_text("             │   ╰────────────────────────────╯   │", fg=fg1, bold=True))
    terminal_print(color_text("        二氧化碳  │   能源  材料  运输     │  高温", fg=fg2, bold=True))
    terminal_print(color_text("             │        ╲      │      ╱             │", fg=fg2, bold=True))
    terminal_print(color_text("             │         ╲     ▼     ╱              │", fg=fg2, bold=True))
    terminal_print(color_text("             │       角向 R             │", fg=fg3, bold=True))
    terminal_print(color_text("             ╰──────────────┬─────────────────────╯", fg=fg1, bold=True))
    terminal_print(color_text("                            ▼", fg=fg1, bold=True))
    terminal_print(color_text("                  契约：有效 / 有条件 / 阻断", fg=(255,255,255), bold=True))
    terminal_print(art_ratio_bar("气候压力代理", clamp(last.worst_boundary_pressure / 1.4), fg3, width=50))


def art_material_cycle(last: GlobalMetrics) -> None:
    art_panel('实质与物质循环', 7, '实质')
    fg = (38, 222, 129)
    terminal_print(color_text("        ┌──────────────┐      ┌──────────────┐      ┌──────────────┐", fg=fg, bold=True))
    terminal_print(color_text("        │  实质 S  │ ───▶ │  生产  │ ───▶ │  使用     │", fg=fg, bold=True))
    terminal_print(color_text("        └──────┬───────┘      └──────┬───────┘      └──────┬───────┘", fg=fg, bold=True))
    terminal_print(color_text("               │                     │                     │", fg=fg, bold=True))
    terminal_print(color_text("               ▼                     ▼                     ▼", fg=fg, bold=True))
    terminal_print(color_text("        ┌──────────────┐      ┌──────────────┐      ┌──────────────┐", fg=(255,214,10), bold=True))
    terminal_print(color_text("        │  修复   │ ◀─── │  废物 Δ    │ ◀─── │  损耗 │", fg=(255,214,10), bold=True))
    terminal_print(color_text("        └──────────────┘      └──────────────┘      └──────────────┘", fg=(255,214,10), bold=True))
    terminal_print(art_ratio_bar("循环指数", last.循环指数, (0,245,212), width=46))
    terminal_print(art_ratio_bar("修复材料", clamp(last.修复材料 / max(1.0, last.修复材料 + last.waste_stock)), (255,106,188), width=46))


def art_commune_network(flows: List[EffectFlow]) -> None:
    art_panel('公社作用网络', 8, '作用')
    selected = top_flows_for_art(flows, 6)
    nodes = ["◉", "◎", "●", "◌", "◍", "◐"]
    for i, flow in enumerate(selected):
        fg = domain_color(flow.domain)
        left = "%s %s/%s" % (nodes[i % len(nodes)], flow.from_region, flow.from_commune)
        right = "%s/%s %s" % (flow.to_region, flow.to_commune, nodes[(i + 2) % len(nodes)])
        arrow = "═" * (8 + (i % 5)) + "▶"
        terminal_print(color_text(left.ljust(34), fg=fg, bold=True) + color_text(arrow, fg=fg, bold=True) + color_text(right, fg=(255,255,255), bold=True))
        terminal_print("    " + domain_badge(flow.domain) + " " + color_text(flow.kind, fg=fg) + " " + color_text("%.2f 作用单位" % flow.activated_effect, fg=(255,240,170), bold=True))
    if not selected:
        terminal_print(color_text("没有作用流。", fg=(255,87,87), bold=True))


def art_products_jobs_services_map() -> None:
    art_panel('产品、工作位置、服务', 9, '真值')
    trio = [
        ("产品", "工具 • 食物 • 水 • 住房 • 医药 • 电池", (255,214,10)),
        ("工作位置", "照护 • 修理 • 农业 • 研究 • 建造 • 能源", (255,106,188)),
        ("服务", "治疗 • 教育 • 运输 • 审计 • 分配 • 照护", (0,229,255)),
        ("生态", "土壤 • 水循环 • 冷却 • 生物多样性 • 栖息地", (38,222,129)),
    ]
    terminal_print(color_text("                 ╭──────────── 作用契约 ────────────╮", fg=(255,255,255), bold=True))
    for name, desc, fg in trio:
        terminal_print(color_text("    ", fg=fg) + styled_badge(name, fg, tuple(int(c*0.20) for c in fg)) + color_text(" ───▶ ", fg=fg, bold=True) + color_text(desc, fg=(245,245,245)))
    terminal_print(color_text("                 ╰────── 真值 + 条件 + 审计 ───╯", fg=(255,255,255), bold=True))


def art_service_constellation() -> None:
    art_panel('服务星座', 10, '纠错')
    center = color_text("       ✦ RE生产 ✦", fg=(255,255,255), bg=(50,20,90), bold=True)
    terminal_print(color_text("             健康", fg=domain_color("health"), bold=True) + "        " + color_text("照护", fg=domain_color("care"), bold=True))
    terminal_print(color_text("                ╲         ╱", fg=(255,106,188), bold=True))
    terminal_print(color_text("                 ╲       ╱", fg=(255,106,188), bold=True))
    terminal_print("                  " + center)
    terminal_print(color_text("                 ╱   │   ╲", fg=(0,229,255), bold=True))
    terminal_print(color_text("        教育         │    流动", fg=(0,229,255), bold=True))
    terminal_print(color_text("                     治理", fg=domain_color("governance"), bold=True))
    terminal_print(color_text("每条边都是作用流：时间、信任、照护、知识、进入。", fg=(245,245,245)))


def art_angle_compass(flow: Optional[EffectFlow]) -> None:
    art_panel('角向罗盘', 11, '自由')
    r = flow.values.get("angle_direction", 3.0) if flow is not None else 3.0
    fg = dim_theme("angle_direction")["fg"]
    terminal_print(color_text("                         ↑ 再生 / 自由", fg=(38,222,129), bold=True))
    terminal_print(color_text("                         │", fg=fg, bold=True))
    terminal_print(color_text("        本地适配 ◀──┼──▶ 星球适配", fg=fg, bold=True))
    terminal_print(color_text("                         │", fg=fg, bold=True))
    terminal_print(color_text("                         ↓ 剥削 / 控制", fg=(255,87,87), bold=True))
    terminal_print(art_ratio_bar("向 角向", r / 4.0, fg, width=52))
    if flow is not None:
        terminal_print(color_text("示例方向：", fg=fg, bold=True) + color_text(flow.direction_vector, fg=(245,245,245)))


def art_difference_funnel(flow: Optional[EffectFlow]) -> None:
    art_panel('差异漏斗', 12, '再生')
    d = flow.values.get("difference", 3.0) if flow is not None else 3.0
    fg = dim_theme("difference")["fg"]
    terminal_print(color_text("        需要 / 困境 / 可能性", fg=(255,255,255), bold=True))
    terminal_print(color_text("      ╱════════════════════════════╲", fg=fg, bold=True))
    terminal_print(color_text("     ╱   住房  食物  照护   ╲", fg=fg, bold=True))
    terminal_print(color_text("    ╱   水  能源  生态    ╲", fg=fg, bold=True))
    terminal_print(color_text("    ╲              Δ                 ╱", fg=fg, bold=True))
    terminal_print(color_text("     ╲       差异被化解          ╱", fg=fg, bold=True))
    terminal_print(color_text("      ╲      作用契约        ╱", fg=fg, bold=True))
    terminal_print(color_text("       ╲═══════════▼═══════════════╱", fg=fg, bold=True))
    terminal_print(color_text("             行动 / 作用", fg=(38,222,129), bold=True))
    terminal_print(art_ratio_bar("D 差异", d / 4.0, fg, width=52))


def art_contract_gate(flow: Optional[EffectFlow]) -> None:
    art_panel('真值契约门', 13, '星球边界')
    validity = flow.contract_validity if flow is not None else "valid"
    score = flow.truth_stack_优先级_0_1 if flow is not None else 0.75
    gates = [
        ("存在", "状态是否真实？", "existence"),
        ("因果", "是否触及原因？", "causality"),
        ("差异", "是否存在真实缺口？", "difference"),
        ("方向", "是否再生/自由？", "angle_direction"),
        ("决定", "是否正当？", "determination"),
    ]
    for name, question, dim in gates:
        fg = dim_theme(dim)["fg"]
        value = flow.values.get(dim, 3.0) if flow is not None else 3.0
        terminal_print(styled_badge(name, fg, dim_theme(dim)["bg"]) + " " + art_ratio_bar(question, value / 4.0, fg, width=38))
    terminal_print(color_text("    ╰──────▶ 结果：", fg=(255,255,255), bold=True) + styled_badge(validity.upper(), (255,255,255), (40,70,40)) + color_text("  优先级 %.3f" % score, fg=(255,214,10), bold=True))


def art_no_money_map() -> None:
    art_panel('无货币核心图', 14, '区域')
    old = ["价格", "价值", "利润", "工资", "租金", "国内总产值", "购买力", "输出价值"]
    new = ["因果", "作用", "差异", "实质", "物质", "决定", "潜能", "方向"]
    for i in range(len(old)):
        terminal_print(styled_badge(old[i], (255,87,87), (70,10,10)) + color_text("  ═══════▶  ", fg=art_color(i), bold=True) + styled_badge(new[i], art_color(i), tuple(int(c*0.20) for c in art_color(i))))


def art_macro_accounts(macro_accounts: List[MacroAccountRow]) -> None:
    art_panel('星球账目', 15, '公社')
    rows = sorted(macro_accounts, key=lambda r: r.优先级, reverse=True)[:8]
    for i, row in enumerate(rows):
        fg = domain_color(row.domain)
        terminal_print(domain_badge(row.domain) + " " + color_text(row.sector, fg=(245,245,245), bold=True))
        terminal_print("  " + art_ratio_bar("满足度", row.满足度, fg, width=36))
        terminal_print("  " + art_ratio_bar("优先级", row.优先级, art_color(i + 3), width=36))
        terminal_print("  " + art_ratio_bar("边界惩罚", row.boundary_penalty, art_color(i + 5), width=36))


def art_ecology_mandala(last: GlobalMetrics) -> None:
    art_panel('生态再生曼荼罗', 16, '群体')
    fg = domain_color("ecology")
    terminal_print(color_text("                  ✺ 土壤 ✺", fg=(190,140,90), bold=True))
    terminal_print(color_text("             ╭──────┼──────╮", fg=fg, bold=True))
    terminal_print(color_text("        水 ─── 🌍 ─── 生物多样性", fg=fg, bold=True))
    terminal_print(color_text("             ╰──────┼──────╯", fg=fg, bold=True))
    terminal_print(color_text("                  ✺ 冷却 ✺", fg=(0,229,255), bold=True))
    terminal_print(color_text("        再生降低风险并提高再生产能力。", fg=(245,245,245)))
    terminal_print(art_ratio_bar("再生产指数", last.planetary_reproduction_index, fg, width=54))


def art_storage_time_bridge(last: GlobalMetrics) -> None:
    art_panel('储备作为时间桥', 17, '个人')
    fg = domain_color("storage")
    terminal_print(color_text("    现在 ────── 食物/水/能源 ──────▶ 以后", fg=fg, bold=True))
    terminal_print(color_text("          ╲                                   ╱", fg=fg, bold=True))
    terminal_print(color_text("           ╲_______ 储存 / 储备 ______╱", fg=fg, bold=True))
    terminal_print(art_ratio_bar("基础缓冲月数", clamp(last.基础缓冲月数 / 6.0), fg, width=52))
    terminal_print(art_ratio_bar("韧性指数", last.韧性指数, (255,166,0), width=52))


def art_governance_feedback(last: GlobalMetrics) -> None:
    art_panel('决定与纠错', 18, '需要')
    fg = domain_color("governance")
    terminal_print(color_text("   受影响者 ──▶ 报告 ──▶ 真值 ──▶ 契约 ──▶ 作用", fg=fg, bold=True))
    terminal_print(color_text("       ▲                                                           │", fg=fg, bold=True))
    terminal_print(color_text("       └──────────── 审计 ◀── 错误检查 ◀── 现象 ◀──────┘", fg=fg, bold=True))
    terminal_print(art_ratio_bar("coordination_quality", last.coordination_quality, fg, width=52))
    terminal_print(art_ratio_bar("真值错误反向值", 1.0 - clamp(last.avg_truth_error), (38,222,129), width=52))


def art_truth_dna(flow: Optional[EffectFlow]) -> None:
    art_panel('真值双螺旋', 19, '实质')
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
    art_panel('领域彩虹', 20, '作用')
    row = ""
    for i, domain in enumerate(DOMAINS):
        row += domain_badge(domain) + " "
        if (i + 1) % 4 == 0:
            terminal_print(row)
            row = ""
    if row:
        terminal_print(row)
    terminal_print(color_text("所有领域共享同样的十二个真值维度，但产品、工作位置和气候要求不同。", fg=(245,245,245)))


def art_resilience_radar(last: GlobalMetrics) -> None:
    art_panel('韧性雷达', 21, '真值')
    metrics = [
        ("水缓冲", clamp(last.water_stock / max(1.0, last.water_stock + last.population * 0.01)), domain_color("water")),
        ("食物缓冲", clamp(last.food_stock / max(1.0, last.food_stock + last.population * 0.01)), domain_color("food")),
        ("能源缓冲", clamp(last.energy_stock / max(1.0, last.energy_stock + last.population * 0.01)), domain_color("energy")),
        ("协调", last.coordination_quality, domain_color("governance")),
        ("自主", last.avg_autonomy, (255,106,188)),
        ("修理", last.循环指数, domain_color("repair")),
    ]
    for name, ratio, fg in metrics:
        terminal_print(art_ratio_bar(name, ratio, fg, width=48))


def art_phenomena_wall(truth_vectors: List[TruthVector]) -> None:
    art_panel('现象墙', 22, '纠错')
    selected = top_truth_for_art(truth_vectors, 8)
    for tv in selected:
        fg = domain_color(tv.domain)
        ph = tv.values.get("phenomena", 0.0)
        terminal_print(domain_badge(tv.domain) + " " + color_text("%s/%s" % (tv.region, tv.commune), fg=(245,245,245), bold=True))
        terminal_print("  " + art_ratio_bar("现象", ph / 4.0, dim_theme("phenomena")["fg"], width=44))
        terminal_print("  " + color_text(terminal_shorten(tv.explanation, 120), fg=(220,220,220)))


def art_potency_garden(truth_vectors: List[TruthVector]) -> None:
    art_panel('潜能花园', 23, '自由')
    selected = top_truth_for_art(truth_vectors, 10)
    for i, tv in enumerate(selected):
        p = tv.values.get("potencies", 0.0)
        flowers = int(round(p))
        fg = dim_theme("potencies")["fg"]
        terminal_print(color_text(("✿" * flowers).ljust(6), fg=fg, bold=True) + domain_badge(tv.domain) + " " + color_text("P=%.2f" % p, fg=fg, bold=True) + " " + color_text(tv.commune, fg=(245,245,245)))


def art_labor_lattice(macro_accounts: List[MacroAccountRow]) -> None:
    art_panel('工作位置格网', 24, '再生')
    rows = sorted(macro_accounts, key=lambda r: r.contribution_time, reverse=True)[:10]
    for i, row in enumerate(rows):
        fg = domain_color(row.domain)
        nodes = max(1, min(18, int(round(row.labor_share * 18))))
        terminal_print(domain_badge(row.domain) + " " + color_text("●─" * nodes + "●", fg=fg, bold=True) + " " + color_text("时间 %.2f" % row.contribution_time, fg=(255,255,255)))


def art_product_wave() -> None:
    art_panel('产品波作为作用载体', 25, '星球边界')
    for i, domain in enumerate(["water", "food", "energy", "shelter", "health", "repair", "ecology", "waste"]):
        fg = domain_color(domain)
        products = TRADE_CATALOG[domain]["products"].split(",")[:5]
        wave = color_text("~≈∿≈~", fg=fg, bold=True)
        terminal_print(domain_badge(domain) + " " + wave + " " + color_text(" | ".join(p.strip() for p in products), fg=(245,245,245)) + " " + wave)


def art_effect_ocean(flows: List[EffectFlow]) -> None:
    art_panel('作用海洋', 26, '区域')
    selected = top_flows_for_art(flows, 12)
    for i, flow in enumerate(selected):
        fg = domain_color(flow.domain)
        height = max(1, min(10, int(round(flow.truth_stack_优先级_0_1 * 10))))
        terminal_print(color_text("≋" * (height + 4), fg=fg, bold=True) + " " + domain_badge(flow.domain) + " " + color_text(flow.kind, fg=(245,245,245)) + " " + color_text("%.2f" % flow.activated_effect, fg=(255,240,170), bold=True))


def art_heatmap_dimensions(flows: List[EffectFlow]) -> None:
    art_panel('契约热图', 27, '公社')
    selected = top_flows_for_art(flows, 8)
    if not selected:
        terminal_print(color_text("没有作用流。", fg=(255,87,87), bold=True))
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
    art_panel('星球经济时间流', 28, '群体')
    wellbeing = [m.wellbeing for m in timeline]
    unmet = [m.unmet_basic for m in timeline]
    overs = [m.overshoot for m in timeline]
    terminal_print(color_text("福祉         ", fg=(38,222,129), bold=True) + art_spark(wellbeing, (38,222,129), width=72))
    terminal_print(color_text("未满足基础需要 ", fg=(255,87,87), bold=True) + art_spark(unmet, (255,87,87), width=72))
    terminal_print(color_text("越界         ", fg=(255,166,0), bold=True) + art_spark(overs, (255,166,0), width=72))


def art_cyberpunk_manifest() -> None:
    art_panel('霓虹宣言', 29, '个人')
    lines = [
        "商品 → 现象",
        "价格 → 真值堆叠",
        "价值 → 作用",
        "数量 → 强度 + 实质",
        "占有 → 使用 + 决定",
        "利润 → 需要和差异化解",
        "市场 → 反馈 + 审计 + 公社",
    ]
    for i, line in enumerate(lines):
        terminal_print(rainbow_text("        ░▒▓█  " + line + "  █▓▒░"))


def art_final_sigil() -> None:
    art_panel('最终印记', 30, '需要')
    colors = art_palette()
    sigil = [
        "                 ╭───────────────╮                 ",
        "             ╭───┤  星球  🌍   ├───╮             ",
        "          ╭──┤   ╰──────┬────────╯   ├──╮          ",
        "       ╭──┤  真值      │   作用   ├──╮       ",
        "       │  ╰──────┬──────┼──────┬──────╯  │       ",
        "       │         ▼      ▼      ▼         │       ",
        "       │      需要  实质  方向 │       ",
        "       │         ▲      ▲      ▲         │       ",
        "       ╰─────────┴──────┴──────┴─────────╯       ",
        "              公社  •  群组  •  个人  ",
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
    art_panel('宏观经济学：星球循环流', 31, '宏观视角：再生产、供给、再生、反馈。')
    art_text_lines(31, [
        '需要 → 贡献 → 作用 → 供给 → 反馈 → 新需要',
        "      ╭───────────────╮      ╭───────────────╮",
        "      │    need      │ ───▶ │ contribution  │",
        "      ╰───────────────╯      ╰───────────────╯",
        "               ▲                       │        ",
        "               │                       ▼        ",
        "      ╭───────────────╮ ◀─── ╭───────────────╮",
        "      │   feedback    │      │    effect     │",
        "      ╰───────────────╯ ───▶ ╰───────────────╯",
        "                    provision / regeneration   ",
        '星球边界包围整个循环。',
        '公社、国家和群组层次出现在作用流之中。',
    ])

def art_macro_provision_balance(last: GlobalMetrics) -> None:
    art_panel('宏观经济学：供给平衡', 32, '不是价格图，而是需要、缺口、再生和越界的状态。')
    art_metric_rows(32, ['福祉', '未满足基本需要', '越界', '星球再生产'], [last.wellbeing, 1.0 - last.unmet_basic, 1.0 - clamp(last.overshoot, 0.0, 1.0), last.planetary_reproduction_index])

def art_macro_sector_web() -> None:
    art_panel('宏观经济学：部门网络', 33, '宏观经济学是作用织体，而不是货币账户。')
    art_text_lines(33, [
        '水 ↔ 食物 ↔ 能源 ↔ 居住 ↔ 健康 ↔ 教育',
        "             water ── food ── energy            ",
        "               ╲        │        ╱              ",
        "                ╲       │       ╱               ",
        "             ecology ─ shelter ─ health         ",
        "                ╱       │       ╲               ",
        "               ╱        │        ╲              ",
        "          repair ── resilience ── education     ",
        '修理和韧性稳定所有领域。',
        '生态不是外部，而是生产和生活基础。',
    ])

def art_macro_domain_matrix() -> None:
    art_panel('宏观经济学：领域矩阵', 34, '每个领域都带有产品、工作位置、服务和气候意义。')
    art_text_lines(34, [
        "┌──────────────┬─────────┬─────────┬─────────┬─────────┐",
        "│ 领域         │ 供给    │ 工作    │ 服务    │ 生态 │",
        "├──────────────┼─────────┼─────────┼─────────┼─────────┤",
        "│ 水           │ ●●●●    │ ●●      │ ●●●     │ ●●●●    │",
        "│ 食物         │ ●●●●    │ ●●●     │ ●●      │ ●●●     │",
        "│ 能源         │ ●●●     │ ●●●     │ ●●      │ ●●      │",
        "│ 健康         │ ●●●     │ ●●●     │ ●●●●    │ ●●      │",
        "│ 修复         │ ●●      │ ●●●●    │ ●●●     │ ●●●      │",
        "└──────────────┴─────────┴─────────┴─────────┴─────────┘",
        '行 = 领域，列 = 供给、工作、服务、生态',
        '宏观协调意味着跨越许多领域关闭真实缺口。',
        '矩阵是彩色的，因为每个领域都有不同的作用颜色。',
    ])

def art_macro_external_trade() -> None:
    art_panel('宏观经济学：没有货币核心的星球外部贸易', 35, '转移意味着区域之间的作用移动，而不是价格套利。')
    art_text_lines(35, [
        '区域甲 ⇄ 区域乙 ⇄ 区域丙',
        "   ┌──────────┐     作用转移      ┌──────────┐",
        "   │ 区域甲 │ ═══════════════════════▶ │ 区域乙 │",
        "   └──────────┘ ◀═══════════════════════ └──────────┘",
        "          ╲                                      ▲   ",
        "           ╲                                     │   ",
        "            ╲══════▶ 区域丙 ◀══════════════════╝   ",
        '输出价值被替换为：化解差异、时间收益、生态作用。',
        '每次转移都携带契约条件和真值。',
    ])

def art_macro_control_cockpit(last: GlobalMetrics) -> None:
    art_panel('宏观经济学：控制驾驶台', 36, '宏观政策读取真值错误、自主、协调和韧性。')
    art_metric_rows(36, ['自主', '协调', '韧性', '真值错误'], [last.avg_autonomy, last.coordination_quality, last.韧性指数, 1.0 - last.avg_truth_error])

def art_macro_regeneration_budget() -> None:
    art_panel('宏观经济学：再生预算', 37, '宏观力量是生命基础的恢复。')
    art_text_lines(37, [
        '土壤 + 水 + 气候 + 生物多样性 + 修理 + 照护',
        "      soil ═══ water ═══ climate ═══ biodiversity   ",
        "         ╲        ╲         │         ╱             ",
        "          ╲        ╲        │        ╱              ",
        "             repair ═══ care ═══ resilience         ",
        '每一项投入都被读作再生方向或损害方向。',
        '最强的经济会修复自身条件。',
    ])

def art_macro_crisis_buffer(last: GlobalMetrics) -> None:
    art_panel('宏观经济学：危机缓冲', 38, '时间、储存、知识和信任是宏观储备。')
    art_metric_rows(38, ['储存逻辑', '知识缓冲', '信任储备', '危机压力'], [last.韧性指数, 1.0 - last.avg_truth_error, last.avg_autonomy, clamp(last.overshoot, 0.0, 1.0)])

def art_business_operating_cycle() -> None:
    art_panel('企业管理：经营作用循环', 39, '采购、生产、服务、维护、修理、回流。')
    art_text_lines(39, [
        '需要 → 计划 → 采购 → 制造 → 检查 → 交付 → 反馈 → 修理',
        "需要 → 计划 → 来源 → 制造 → 测试 → 交付 → 服务 → 修复",
        "  ▲                                                     │       ",
        "  └────────────── 反馈与学习 ────────────────┘       ",
        '组织是作用器官，不只是货币机器。',
        '企业管理变成可见的过程架构。',
    ])

def art_business_capability_house() -> None:
    art_panel('企业管理：能力之屋', 40, '人员、工具、知识、时间和基础设施构成企业之屋。')
    art_text_lines(40, [
        "                 /\\                                   ",
        "                /  \\                                  ",
        "               /____\\                                 ",
        "              |      |                                 ",
        "              | 数据 | 服务 | 制造 | 照护 |       ",
        "              |______|_________|_______|______|        ",
        "              | 真值 | 实质 | 物质 | 安全 |  ",
        '屋顶：目的和方向',
        '房间：采购、制造、照护、服务、数据、学习',
        '基础：真值、决定、实质、物质、安全',
    ])

def art_business_process_chain() -> None:
    art_panel('企业管理：过程链', 41, '从订单到作用：每一步都有条件。')
    art_text_lines(41, [
        '订单 → 需要澄清 → 因果检查 → 工作计划 → 执行 → 审计 → 交付',
        "[订单]→[澄清]→[原因]→[计划]→[执行]→[审计]→[交付]",
        "     ╰───────────── 质量与反馈回流 ─────────────╯  ",
        '质量通过反馈形成，而不是只在最后。',
        '链条是彩色的，因为许多专业角色共同合作。',
    ])

def art_business_quality_loop() -> None:
    art_panel('企业管理：质量回路', 42, '观察、测量、纠正、再测、放行。')
    art_text_lines(42, [
        '现象 → 测量 → 比较 → 纠正 → 记录 → 新真值',
        "观察 → 测量 → 比较 → 纠正 → 记录 → 放行",
        "   ▲                                                    │      ",
        "   └──────────────── 新真值与新检查 ───────────┘      ",
        '质量不是边角话题，而是运动中的契约真值。',
        '回路防止错误变成损害。',
    ])

def art_business_inventory_buffers(last: GlobalMetrics) -> None:
    art_panel('企业管理：库存和缓冲逻辑', 43, '库存是时间桥梁和供给盾牌。')
    art_metric_rows(43, ['材料缓冲', '能源缓冲', '时间缓冲', '修理储备'], [last.韧性指数, max(0.0, min(1.0, 0.55 + 0.35 * last.planetary_reproduction_index)), max(0.0, min(1.0, 0.45 + 0.45 * last.coordination_quality)), max(0.0, min(1.0, 0.40 + 0.45 * last.韧性指数))])

def art_business_project_portfolio() -> None:
    art_panel('企业管理：项目组合', 44, '重要和紧急项目在真值条件下竞争。')
    art_text_lines(44, [
        "                    importance                           ",
        "                     high                               ",
        "            ┌───────────────────────┬──────────────────┐",
        "            │ regenerative core     │ urgent repair    │",
        " urgency    │ and care              │ and protection   │",
        "  high      ├───────────────────────┼──────────────────┤",
        "            │ transformative build  │ later reserve    │",
        "            │ and learning          │ and observation  │",
        "            └───────────────────────┴──────────────────┘",
        '象限：紧急/重要、紧急/稍后、再生/变革',
        '项目选择不仅遵循回报，也遵循作用和边界保护。',
        '组合控制因此变得社会可读。',
    ])

def art_business_risk_canvas() -> None:
    art_panel('企业管理：风险画布', 45, '气候风险、供应链、真值、接受度、技术、健康。')
    art_text_lines(45, [
        "┌──────────────┬──────────────┬──────────────┐",
        f"│ 低            │ 中            │ 高            │",
        "├──────────────┼──────────────┼──────────────┤",
        f"│ 气候           │ 低            │ 中            │",
        f"│ 物流           │ 中            │ 高            │",
        f"│ 真值           │ 低            │ 中            │",
        f"│ 接受度          │ 中            │ 中            │",
        f"│ 技术           │ 低            │ 中            │",
        f"│ 健康           │ 低            │ 中            │",
        "└──────────────┴──────────────┴──────────────┘",
        '风险来源在造成损害之前被显示出来。',
        '管理谨慎意味着尽早看到条件。',
        '颜色标记低、中、高危险。',
    ])

def art_business_service_blueprint() -> None:
    art_panel('企业管理：服务蓝图', 46, '接触点、报告、处理、作用、后续照护。')
    art_text_lines(46, [
        '个人报告需要 → 团队记录 → 系统检查 → 激活作用 → 后续照护',
        "个人 → 接收 → 验证 → 激活 → 照护 → 学习",
        "   │         │          │             │          │         │   ",
        " 报告     接触点     系统          作用       服务      复核  ",
        '服务表现为有组织的照护和问题解决。',
        '在底部，这条链又回到学习和改进。',
    ])
def print_utf8_art_gallery_terminal(flows: List[EffectFlow], truth_vectors: List[TruthVector], timeline: List[GlobalMetrics], macro_accounts: List[MacroAccountRow], limit: int = 46) -> None:
    if limit <= 0:
        return
    terminal_header('极端彩色统一码图画廊', '契约下方的显示：图表、图像、循环、罗盘、热图、宏观经济学和企业管理。')
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
    parser = argparse.ArgumentParser(description='用于星球作用经济、契约和真值维度的彩色终端显示', add_help=False)
    parser.add_argument('--帮助', action="help", help='显示帮助并退出')
    parser.add_argument('--步数', dest="steps", type=int, default=120, help='模拟月数')
    parser.add_argument('--种子', dest="seed", type=int, default=42, help='随机种子')
    parser.add_argument('--人口', dest="population", type=float, default=8_100_000_000.0, help='合成人口')
    parser.add_argument('--区域数', dest="regions", type=int, default=12, help='生物区域数量')
    parser.add_argument('--每区公社', dest="communes_per_region", type=int, default=8, help='每区公社数量')
    parser.add_argument('--方案', dest="scenario", choices=('星球共有', '地方民主', '技术管制', '生态危机', '短缺冲击'), default='星球共有', help='方案')
    parser.add_argument('--输出', dest="out", default='星球输出_中文', help='输出目录')
    parser.add_argument('--安静', dest="quiet", action="store_true", help='不打印最终摘要')
    parser.add_argument('--显示交易', dest="show_trades", type=int, default=16, help='可见契约')
    parser.add_argument('--显示细节', dest="show_trade_detail", action="store_true", help='完整契约细节')
    parser.add_argument('--显示维度', dest="show_dimensions", action="store_true", help='维度指南')
    parser.add_argument('--显示目录', dest="show_catalog", action="store_true", help='目录')
    parser.add_argument('--显示堆叠说明', dest="show_stack_explanation", action="store_true", help='堆叠说明')
    parser.add_argument('--显示图画', dest="show_art", type=int, default=46, help='统一码图画数量')
    parser.add_argument('--强制颜色', dest="force_color", action="store_true", help='强制颜色')
    parser.add_argument('--无颜色', dest="no_color", action="store_true", help='关闭颜色')
    parser.add_argument('--宽度', dest="width", type=int, default=0, help='强制终端宽度')
    return parser.parse_args(argv)

def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    set_forced_terminal_width(getattr(args, "width", 0))
    set_terminal_color_enabled((not args.no_color) and (args.force_color or ((os.environ.get("NO_COLOR") is None) and sys.stdout.isatty())))
    if args.steps < 0:
        raise SystemExit('--步数必须大于或等于 0')
    if args.population <= 0:
        raise SystemExit('--人口必须大于 0')
    if args.regions <= 0 or args.communes_per_region <= 0:
        raise SystemExit('--区域数和--每区公社必须大于 0')
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
        pretty_key_value(localized_label("resilience"), "%.4f -> %.4f (Δ %.4f)" % (first.韧性指数, last.韧性指数, last.韧性指数 - first.韧性指数), label_fg=(190, 140, 90))
        pretty_key_value(localized_label("coordination"), "%.4f -> %.4f (Δ %.4f)" % (first.coordination_quality, last.coordination_quality, last.coordination_quality - first.coordination_quality), label_fg=(255, 106, 188))
        pretty_key_value(localized_label("inequality"), "%.4f -> %.4f (Δ %.4f)" % (first.满足度_inequality, last.满足度_inequality, last.满足度_inequality - first.满足度_inequality), label_fg=(120, 185, 255))
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
