"""The complete MCM-only skill namespace shipped by this repository."""

CORE_SKILLS = (
    'mcm-suite', 'mcm-problem-analyst', 'mcm-method-retriever',
    'mcm-data-researcher', 'mcm-model-designer', 'mcm-python-coder',
    'mcm-matlab-coder', 'mcm-result-verifier', 'mcm-paper-writer',
    'mcm-layout-verifier', 'mcm-final-auditor',
)
MODEL_FAMILIES = (
    'control', 'discrete', 'evaluation', 'games', 'inverse',
    'machine-learning', 'mechanisms', 'numerical', 'optimization',
    'signals-images', 'simulation', 'statistics', 'time-series',
)
EXPECTED_SKILLS = CORE_SKILLS + tuple(
    'mcm-modeling-' + name for name in ('library', 'paper-writing') + MODEL_FAMILIES
)
EXPECTED_CARD_COUNT = 198
