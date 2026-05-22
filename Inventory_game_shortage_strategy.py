import streamlit as st
import random
import pandas as pd
import altair as alt
import textwrap
import requests
import re
from datetime import datetime, timezone
from html import escape as html_escape
from streamlit.components.v1 import html


st.set_page_config(page_title="Spare Parts ROP / EOQ Planning Game", layout="wide")


# =========================================================
# SECTION 1: CUSTOM STYLING
# =========================================================

st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(95, 76, 196, 0.35), transparent 28%),
            radial-gradient(circle at top right, rgba(41, 160, 255, 0.20), transparent 22%),
            linear-gradient(180deg, #0d1430 0%, #12193a 45%, #10162d 100%);
        color: #f4f7ff;
    }

    .block-container {
        padding-top: 1.0rem;
        padding-bottom: 1rem;
        max-width: 1500px;
    }

    h1, h2, h3, p, li, label {
        color: #ffffff !important;
    }

    div[data-testid="stAlert"] {
        background: rgba(245, 248, 255, 0.96);
        border: 1px solid rgba(191, 250, 244, 0.28);
        border-radius: 12px;
    }

    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] li,
    div[data-testid="stAlert"] div {
        color: #111827 !important;
    }

    div[data-testid="stDialog"] p,
    div[data-testid="stDialog"] li,
    div[data-testid="stDialog"] label {
        color: #111827 !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(9, 18, 48, 0.75);
        border: 1px solid rgba(120, 140, 255, 0.18);
        border-radius: 16px;
        padding: 12px 14px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.18);
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricDelta"] {
        color: #ffffff !important;
    }

    .dashboard-panel {
        background: rgba(7, 14, 35, 0.80);
        border: 1px solid rgba(120, 140, 255, 0.18);
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.22);
        margin-bottom: 14px;
    }

    .top-title-card {
        background: linear-gradient(90deg, rgba(21,31,72,0.95), rgba(14,20,53,0.9));
        border: 1px solid rgba(132, 156, 255, 0.18);
        border-radius: 18px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.24);
    }

    .top-title {
        font-size: 2rem;
        font-weight: 800;
        color: white;
        margin-bottom: 4px;
    }

    .top-subtitle {
        color: #ffffff;
        font-size: 1rem;
        margin-bottom: 0;
    }

    .cost-box {
        background: rgba(9, 20, 52, 0.92);
        border: 1px solid rgba(113, 145, 255, 0.20);
        border-radius: 16px;
        padding: 14px 18px;
        color: #eef2ff;
        margin-bottom: 14px;
    }

    .cost-chip {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 10px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.08);
        margin-right: 8px;
        margin-top: 6px;
        font-family: monospace;
        font-size: 0.95rem;
        color: white;
    }

    .small-note {
        color: #ffffff;
        font-size: 0.95rem;
    }

    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        border: none;
        min-height: 2.5rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
        margin-top: 6px;
    }

    .report-hero {
        border: 1px solid rgba(191,250,244,0.22);
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 16px;
        background:
            linear-gradient(135deg, rgba(21,31,72,0.96), rgba(7,14,35,0.94)),
            radial-gradient(circle at top right, rgba(69,208,197,0.16), transparent 28%);
        box-shadow: 0 16px 36px rgba(0,0,0,0.26);
    }

    .report-eyebrow {
        color: #bffaf4;
        font-size: 0.78rem;
        font-weight: 900;
        letter-spacing: 0;
        text-transform: uppercase;
    }

    .report-title {
        color: #ffffff;
        font-size: 1.7rem;
        font-weight: 900;
        margin-top: 4px;
    }

    .report-subtitle {
        color: #d8def7;
        font-size: 0.96rem;
        margin-top: 5px;
    }

    .scorecard-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 14px 0 18px;
    }

    .scorecard {
        background: rgba(8, 17, 43, 0.92);
        border: 1px solid rgba(120, 140, 255, 0.18);
        border-radius: 14px;
        padding: 13px 14px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.20);
    }

    .scorecard.player {
        border-color: rgba(255,223,107,0.42);
        background: linear-gradient(180deg, rgba(40,35,23,0.95), rgba(8,17,43,0.92));
    }

    .scorecard-policy {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .scorecard-row {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 7px;
        margin-top: 7px;
        color: #d8def7;
        font-size: 0.86rem;
    }

    .scorecard-row strong {
        color: #ffffff;
    }

    .penalty-overview-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 12px 0 16px;
    }

    .penalty-card {
        border: 1px solid rgba(255,223,107,0.28);
        border-radius: 16px;
        padding: 14px 16px;
        background: linear-gradient(135deg, rgba(31,43,86,0.95), rgba(8,17,43,0.94));
        box-shadow: 0 12px 28px rgba(0,0,0,0.22);
    }

    .penalty-card.player {
        border-color: rgba(255,223,107,0.58);
        background: linear-gradient(135deg, rgba(68,38,18,0.96), rgba(8,17,43,0.94));
    }

    .penalty-card-title {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 900;
    }

    .penalty-card-value {
        color: #ffdf6b;
        font-size: 2.2rem;
        font-weight: 950;
        line-height: 1.05;
        margin-top: 8px;
    }

    .penalty-card-note {
        color: #d8def7;
        font-size: 0.88rem;
        margin-top: 8px;
    }

    .chart-panel {
        border: 1px solid rgba(120, 140, 255, 0.16);
        border-radius: 14px;
        padding: 12px 14px;
        background: rgba(255,255,255,0.04);
        margin-bottom: 14px;
    }

    .chart-title {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .report-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        overflow: hidden;
        border: 1px solid rgba(120,140,255,0.20);
        border-radius: 12px;
        color: #eef2ff;
        font-size: 0.92rem;
    }

    .report-table th {
        background: rgba(18, 29, 68, 0.98);
        color: #ffffff;
        padding: 11px 12px;
        text-align: left;
        border-bottom: 1px solid rgba(255,255,255,0.10);
        font-weight: 900;
    }

    .report-table td {
        background: rgba(8, 17, 43, 0.86);
        color: #d8def7;
        padding: 10px 12px;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }

    .report-table tr:last-child td {
        border-bottom: none;
    }

    .report-table td.number {
        text-align: right;
        font-variant-numeric: tabular-nums;
        color: #ffffff;
    }

    .report-table td.policy-player {
        color: #ffdf6b;
        font-weight: 900;
    }

    .report-table td.cost-high {
        background: rgba(255, 59, 59, 0.20);
    }

    .report-table td.fill-good {
        background: rgba(69, 208, 197, 0.18);
    }

    .report-table td.fill-low {
        background: rgba(255, 107, 107, 0.18);
    }

    .scenario-ribbon {
        position: fixed;
        top: 140px;
        left: 0;
        writing-mode: vertical-rl;
        text-orientation: mixed;
        z-index: 999;
        padding: 24px 13px;
        border-radius: 0 16px 16px 0;
        background: linear-gradient(180deg, rgba(255,223,107,0.96), rgba(69,208,197,0.96));
        color: #07101f;
        font-weight: 900;
        font-size: 1.08rem;
        box-shadow: 0 12px 30px rgba(0,0,0,0.28);
        letter-spacing: 0;
    }

    .decision-panel {
        border: 1px solid rgba(255,223,107,0.30);
        border-radius: 16px;
        padding: 14px 16px;
        margin: 14px 0 16px;
        background: linear-gradient(135deg, rgba(40,35,23,0.88), rgba(8,17,43,0.92));
        box-shadow: 0 12px 28px rgba(0,0,0,0.24);
    }

    .decision-panel-title {
        color: #ffdf6b;
        font-weight: 900;
        font-size: 1.05rem;
        margin-bottom: 6px;
    }

    .decision-row-label {
        color: #d8def7;
        font-size: 0.82rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .decision-month-pill {
        height: 100%;
        min-height: 72px;
        border: 1px solid rgba(255,223,107,0.26);
        border-radius: 14px;
        background: rgba(255,223,107,0.10);
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 10px 12px;
    }

    .decision-month-pill span {
        color: #ffdf6b;
        font-size: 0.78rem;
        font-weight: 900;
    }

    .decision-month-pill strong {
        color: #ffffff;
        font-size: 1.45rem;
        font-weight: 900;
    }

    .round2-ribbon-marker {
        display: none;
    }

    div[data-testid="stElementContainer"]:has(.round2-ribbon-marker) + div[data-testid="stElementContainer"] div.stButton {
        position: fixed;
        top: 4vh;
        right: 0;
        z-index: 1000;
        height: 92vh;
        width: 46px;
    }

    div[data-testid="stElementContainer"]:has(.round2-ribbon-marker) + div[data-testid="stElementContainer"] div.stButton > button {
        width: 46px;
        height: 92vh;
        padding: 18px 13px;
        border-radius: 16px 0 0 16px;
        background: linear-gradient(180deg, #ff4d5a, #ffdf6b);
        color: #07101f !important;
        font-size: 1.12rem;
        font-weight: 900;
        box-shadow: 0 0 0 rgba(255,223,107,0.55);
        animation: continuePulse 1.1s infinite;
        display: flex;
        align-items: center;
        justify-content: center;
        writing-mode: vertical-rl;
        text-orientation: mixed;
        cursor: pointer;
        border: none;
    }

    div[data-testid="stElementContainer"]:has(.round2-ribbon-marker) + div[data-testid="stElementContainer"] div.stButton > button:hover {
        color: #07101f !important;
        filter: brightness(1.06);
    }

    @keyframes continuePulse {
        0% { box-shadow: 0 0 0 0 rgba(255,223,107,0.68); transform: translateX(0); }
        50% { box-shadow: 0 0 26px 8px rgba(255,223,107,0.38); transform: translateX(-3px); }
        100% { box-shadow: 0 0 0 0 rgba(255,223,107,0.0); transform: translateX(0); }
    }

    .round-complete-card {
        border: 1px solid rgba(255,223,107,0.36);
        border-radius: 20px;
        padding: 20px;
        background:
            radial-gradient(circle at top right, rgba(255,223,107,0.16), transparent 26%),
            linear-gradient(135deg, rgba(34,29,14,0.96), rgba(8,17,43,0.96));
        box-shadow: 0 18px 42px rgba(0,0,0,0.28);
        margin-bottom: 18px;
    }

    .round-complete-title {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 900;
        margin-bottom: 6px;
    }

    .round-complete-text {
        color: #d8def7;
        font-size: 1rem;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        min-height: 3rem;
        font-size: 1rem;
    }

    .intro-shell {
        border: 1px solid rgba(191,250,244,0.24);
        border-radius: 20px;
        padding: 18px 20px;
        margin-bottom: 18px;
        background:
            radial-gradient(circle at top right, rgba(69,208,197,0.18), transparent 28%),
            linear-gradient(135deg, rgba(17,28,69,0.96), rgba(8,16,42,0.96));
        box-shadow: 0 18px 42px rgba(0,0,0,0.28);
    }

    .intro-kicker {
        color: #bffaf4;
        font-size: 0.78rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0;
    }

    .intro-heading {
        color: #ffffff;
        font-size: 1.85rem;
        font-weight: 900;
        margin-top: 5px;
        margin-bottom: 8px;
    }

    .intro-copy {
        color: #d8def7;
        font-size: 1rem;
        line-height: 1.55;
        max-width: 980px;
    }

    .intro-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin-top: 16px;
    }

    .intro-step {
        border: 1px solid rgba(120,140,255,0.18);
        border-radius: 14px;
        background: rgba(255,255,255,0.055);
        padding: 13px 14px;
        min-height: 138px;
    }

    .intro-step-number {
        width: 28px;
        height: 28px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255,223,107,0.18);
        color: #ffdf6b;
        font-weight: 900;
        margin-bottom: 9px;
    }

    .intro-step-title {
        color: #ffffff;
        font-weight: 900;
        font-size: 0.96rem;
        margin-bottom: 5px;
    }

    .intro-step-text {
        color: #d8def7;
        font-size: 0.88rem;
        line-height: 1.4;
    }

    @media (max-width: 900px) {
        .intro-grid,
        .scorecard-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# SECTION 2: CONFIGURATION
# =========================================================

class Config:
    def __init__(self):
        self.months = 12

        # Item-specific planning parameters
        self.item_planning_parameters = {
            "Item 1 - Slow / uncertain spare part": {
                "initial_inventory": 4,
                "initial_rop": 2,
                "eoq": 3,
            },
            "Item 2 - Stable / high sales item": {
                "initial_inventory": 40,
                "initial_rop": 27,
                "eoq": 50,
            },
        }

        # Historical demand used for the 2025 reference period
        self.item_last_year_demand = {
            "Item 1 - Slow / uncertain spare part": [2, 0, 0, 5, 2, 0, 1, 0, 0, 8, 0, 1],
            "Item 2 - Stable / high sales item": [26, 28, 27, 30, 29, 31, 28, 27, 30, 29, 28, 31],
        }
        self.slow_uncertain_demand_ranges = [
            0,
            (2, 3),
            (1, 2),
            (9, 10),
            (7, 8),
            (5, 6),
            0,
            (3, 4),
            (6, 7),
            (2, 3),
            (1, 2),
            0,
        ]

        # Changing lead time logic:
        # Month 1-2 = 1 month
        # Month 3-7 = 3 months
        # Month 8+  = 1 month
        self.initial_lead_time = 1
        self.shock_month = 3
        self.shocked_lead_time = 3
        self.partial_recovery_month = 7
        self.partial_recovery_lead_time = 2
        self.full_recovery_month = 8
        self.recovered_lead_time = 1

        self.random_seed = 42

        self.holding_cost_per_unit = 5.0
        self.backlog_cost_per_unit = 20.0
        self.supplier_agreement_monthly_fee = 50.0
        self.air_freight_cost_per_unit = 35.0

        self.items = {
            "Item 1 - Slow / uncertain spare part": {
                "description": "Very slow and uncertain demand. Some months have zero demand and one exceptional demand spike.",
                "demand_type": "slow_uncertain",
            },
            "Item 2 - Stable / high sales item": {
                "description": "Stable and higher demand. Demand is more predictable, but the lead-time shock can still create risk.",
                "demand_type": "stable_high",
            },
        }

        self.game_variants = [
            {
                "item": "Item 1 - Slow / uncertain spare part",
                "lead_time_mode": "changing",
                "title": "Slow mover - changing lead time",
                "intro": "You are going to play the old slow-moving spare part scenario where lead time can change during the game. Watch for the lead-time messages and adjust your ROP when the supply situation changes.",
                "cost_strategy": "none",
            },
            {
                "item": "Item 1 - Slow / uncertain spare part",
                "lead_time_mode": "changing",
                "title": "Round 2 - supplier agreement",
                "intro": "You chose a supplier agreement. The market lead time can still be shocked, but the supplier keeps reserved stock for us so our effective replenishment lead time stays at 1 month. The supplier charges 50 per month, included in total cost.",
                "cost_strategy": "supplier_agreement",
            },
            {
                "item": "Item 1 - Slow / uncertain spare part",
                "lead_time_mode": "changing",
                "title": "Round 2 - air freight",
                "intro": "You chose air freight. When the normal lead time is shocked to 3 months, every replenishment PO is expedited so the effective lead time becomes 1 month. It is not instant replenishment: an order placed this month arrives next month. Air freight costs 35 per expedited PO unit and is included in total cost.",
                "cost_strategy": "air_freight",
            },
        ]

    def get_item_initial_inventory(self, item_name):
        return self.item_planning_parameters[item_name]["initial_inventory"]

    def get_item_initial_rop(self, item_name):
        return self.item_planning_parameters[item_name]["initial_rop"]

    def get_item_eoq(self, item_name):
        return self.item_planning_parameters[item_name]["eoq"]

    def lead_time(self, month, lead_time_mode="changing"):
        if lead_time_mode == "constant":
            return self.initial_lead_time
        if month >= self.full_recovery_month:
            return self.recovered_lead_time
        if month >= self.shock_month:
            return self.shocked_lead_time
        return self.initial_lead_time

    def demand(self, month, item_name):
        demand_type = self.items[item_name]["demand_type"]
        rng = random.Random(self.random_seed + month)

        if demand_type == "slow_uncertain":
            demand_value = self.slow_uncertain_demand_ranges[month - 1] if 1 <= month <= len(self.slow_uncertain_demand_ranges) else 0
            if isinstance(demand_value, tuple):
                return rng.choice(list(range(demand_value[0], demand_value[1] + 1)))
            return demand_value

        if demand_type == "stable_high":
            # More challenging high-volume demand pattern with seasonality and spikes.
            demand_pattern = {
                1: 24,
                2: 34,
                3: 27,
                4: 45,
                5: 39,
                6: 31,
                7: 52,
                8: 28,
                9: 36,
                10: 48,
                11: 33,
                12: 29,
                13: 43,
                14: 35,
                15: 55,
                16: 30,
                17: 41,
                18: 37,
            }
            return demand_pattern.get(month, rng.randint(30, 45))

        return 0

    def sample_demand_series(self, item_name):
        demand_type = self.items[item_name]["demand_type"]
        if demand_type == "slow_uncertain":
            rng = random.SystemRandom()
            values = []
            for demand_value in self.slow_uncertain_demand_ranges[:self.months]:
                if isinstance(demand_value, tuple):
                    values.append(rng.randint(demand_value[0], demand_value[1]))
                else:
                    values.append(demand_value)
            return values
        return [self.demand(month, item_name) for month in range(1, self.months + 1)]


cfg = Config()
APP_VERSION = "slow_mover_random_ranges_no_old_endpoint_v1"
TARGET_FILL_RATE_PERCENT = 85.0
FILL_RATE_PENALTY_PER_PERCENT = 100.0
OVERSTOCK_PENALTY_PER_UNIT = 20.0

BIGQUERY_SCRIPT_URL_PLACEHOLDER = "https://script.google.com/macros/s/AKfycbwvAwn4xdYarourBnqqZhzc8eokVAq4uEweITj-7Uy1vnP1moxyq9jzpCx_i5ddR_b_/exec"
BIGQUERY_SCRIPT_URL = BIGQUERY_SCRIPT_URL_PLACEHOLDER
ADMIN_REPORT_EMAIL = "mohsen.adelfar@hiab.com"


# =========================================================
# SECTION 3: STATE
# =========================================================

def init_game():
    variant_index = st.session_state.get("variant_index", 0)
    selected_variant = cfg.game_variants[variant_index]
    selected_item = selected_variant["item"]
    st.session_state.selected_item = selected_item
    st.session_state.lead_time_mode = selected_variant["lead_time_mode"]
    st.session_state.cost_strategy = selected_variant.get("cost_strategy", "none")
    st.session_state.scenario_title = selected_variant["title"]
    st.session_state.scenario_intro = selected_variant["intro"]
    st.session_state.month = 1
    st.session_state.inventory = cfg.get_item_initial_inventory(selected_item)
    st.session_state.pipeline = []
    st.session_state.backlog = 0
    st.session_state.cumulative_cost = 0.0
    st.session_state.history = []
    st.session_state.game_demand = cfg.sample_demand_series(selected_item)
    st.session_state.submitted = False
    st.session_state.current_rop = cfg.get_item_initial_rop(selected_item)
    st.session_state.scenario_notice_seen = False
    st.session_state.report_saved_current = False
    st.session_state.lead_time_event_seen = []
    st.session_state.round_complete_seen = False
    st.session_state.second_round_popup_step = None
    st.session_state.submission_warning = None


if "player_ready" not in st.session_state:
    st.session_state.player_ready = False
    st.session_state.player_name = ""
    st.session_state.player_email = ""
    st.session_state.variant_index = 0
    st.session_state.completed_reports = []
    st.session_state.selected_item = cfg.game_variants[0]["item"]
    st.session_state.lead_time_mode = cfg.game_variants[0]["lead_time_mode"]
    st.session_state.scenario_title = cfg.game_variants[0]["title"]
    st.session_state.scenario_intro = cfg.game_variants[0]["intro"]
    st.session_state.cost_strategy = cfg.game_variants[0].get("cost_strategy", "none")
    st.session_state.second_round_popup_step = None

if st.session_state.get("shortage_strategy_app_version") != APP_VERSION:
    preserved_name = st.session_state.get("player_name", "")
    preserved_email = st.session_state.get("player_email", "")
    st.session_state.player_ready = False
    st.session_state.player_name = preserved_name
    st.session_state.player_email = preserved_email
    st.session_state.variant_index = 0
    st.session_state.completed_reports = []
    st.session_state.selected_item = cfg.game_variants[0]["item"]
    st.session_state.lead_time_mode = cfg.game_variants[0]["lead_time_mode"]
    st.session_state.cost_strategy = cfg.game_variants[0].get("cost_strategy", "none")
    st.session_state.scenario_title = cfg.game_variants[0]["title"]
    st.session_state.scenario_intro = cfg.game_variants[0]["intro"]
    st.session_state.second_round_popup_step = None
    st.session_state.shortage_strategy_app_version = APP_VERSION

migrating_to_variant_flow = "variant_index" not in st.session_state
if migrating_to_variant_flow:
    st.session_state.variant_index = 0

active_variant = cfg.game_variants[st.session_state.variant_index]
if "completed_reports" not in st.session_state:
    st.session_state.completed_reports = []
if "second_round_popup_step" not in st.session_state:
    st.session_state.second_round_popup_step = None
if migrating_to_variant_flow or "selected_item" not in st.session_state:
    st.session_state.selected_item = active_variant["item"]
if migrating_to_variant_flow or "lead_time_mode" not in st.session_state:
    st.session_state.lead_time_mode = active_variant["lead_time_mode"]
if migrating_to_variant_flow or "cost_strategy" not in st.session_state:
    st.session_state.cost_strategy = active_variant.get("cost_strategy", "none")
if migrating_to_variant_flow or "scenario_title" not in st.session_state:
    st.session_state.scenario_title = active_variant["title"]
if migrating_to_variant_flow or "scenario_intro" not in st.session_state:
    st.session_state.scenario_intro = active_variant["intro"]
if "scenario_notice_seen" not in st.session_state:
    st.session_state.scenario_notice_seen = False
if "report_saved_current" not in st.session_state:
    st.session_state.report_saved_current = False
if "lead_time_event_seen" not in st.session_state:
    st.session_state.lead_time_event_seen = []
if "round_complete_seen" not in st.session_state:
    st.session_state.round_complete_seen = False
if "submitted_scenario_keys" not in st.session_state:
    st.session_state.submitted_scenario_keys = []

if migrating_to_variant_flow and st.session_state.get("player_ready", False):
    init_game()

if "month" not in st.session_state:
    init_game()
if "game_demand" not in st.session_state:
    st.session_state.game_demand = cfg.sample_demand_series(st.session_state.selected_item)

# =========================================================
# SECTION 4: HELPERS
# =========================================================

MONTH_NAMES_12 = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

MONTH_LABELS_20 = [
    "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026",
    "Jun 2026", "Jul 2026", "Aug 2026", "Sep 2026", "Oct 2026",
    "Nov 2026", "Dec 2026", "Jan 2027", "Feb 2027", "Mar 2027",
    "Apr 2027", "May 2027", "Jun 2027", "Jul 2027", "Aug 2027"
]


def valid_email(email):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()) is not None


def pipeline_total():
    return sum(x["qty"] for x in st.session_state.pipeline)


def inventory_position():
    # Inventory Position = On-hand stock + On-order stock - Backorders.
    # In this game, backlog represents backorders.
    return st.session_state.inventory + pipeline_total() - st.session_state.backlog


def current_lead_time_mode():
    return st.session_state.get("lead_time_mode", "changing")


def current_cost_strategy():
    return st.session_state.get("cost_strategy", "none")


def effective_lead_time_for_strategy(base_lead_time, cost_strategy=None):
    strategy = cost_strategy if cost_strategy is not None else current_cost_strategy()
    if strategy == "supplier_agreement":
        return 1
    if strategy == "air_freight" and base_lead_time > 1:
        return 1
    return base_lead_time


def strategy_cost_explanation(cost_strategy=None):
    strategy = cost_strategy if cost_strategy is not None else current_cost_strategy()
    if strategy == "supplier_agreement":
        return (
            f"Supplier agreement: the supplier keeps reserved stock for us, so effective replenishment lead time stays at 1 month. "
            f"Cost = {cfg.supplier_agreement_monthly_fee:,.0f} per month, added to total cost every month."
        )
    if strategy == "air_freight":
        return (
            f"Air freight: only during the 3-month lead-time shock, replenishment POs are expedited to a 1-month lead time. "
            f"It is not instant replenishment: an order placed this month arrives next month. "
            f"Cost = {cfg.air_freight_cost_per_unit:,.0f} per expedited PO unit, added to total cost in that month."
        )
    return "No extra strategy cost. Total cost includes inventory holding cost and backlog cost."


def second_round_options():
    return [
        (
            1,
            "Supplier agreement",
            "Pay the supplier every month to keep reserved stock for us. The supplier absorbs the raw-material shortage risk, so our effective lead time stays at 1 month.",
            strategy_cost_explanation("supplier_agreement"),
        ),
        (
            2,
            "Air freight",
            "Use air freight only when the normal lead time is shocked to 3 months. Replenishment POs arrive after 1 month, not immediately, and air-freight cost is charged per expedited PO unit.",
            strategy_cost_explanation("air_freight"),
        ),
    ]


def get_game_month_label(month_number):
    if 1 <= month_number <= len(MONTH_LABELS_20):
        return MONTH_LABELS_20[month_number - 1]
    return f"Month {month_number}"


def get_historical_demand_df(item_name):
    return pd.DataFrame({
        "Month": MONTH_NAMES_12,
        "Demand": cfg.item_last_year_demand[item_name]
    })


def get_rop_advice(item_name):
    historical_demand = pd.Series(cfg.item_last_year_demand[item_name])
    average_monthly_demand = historical_demand.mean()
    demand_std_dev = historical_demand.std(ddof=0)
    average_lead_time = 1
    z_value = 1
    expected_lead_time_demand = average_monthly_demand * average_lead_time
    safety_stock = z_value * demand_std_dev
    recommended_rop = max(0, round(expected_lead_time_demand + safety_stock))

    return {
        "average_monthly_demand": average_monthly_demand,
        "average_lead_time": average_lead_time,
        "z_value": z_value,
        "demand_std_dev": demand_std_dev,
        "expected_lead_time_demand": expected_lead_time_demand,
        "safety_stock": safety_stock,
        "recommended_rop": recommended_rop,
    }


def calculate_actual_stockmax_benchmark(df):
    actual_demand = pd.Series(df["New Demand"])
    lead_time_column = "Effective Lead Time" if "Effective Lead Time" in df.columns else "Lead Time"
    actual_lead_time = pd.Series(df[lead_time_column])
    average_monthly_demand = actual_demand.mean()
    end_lead_time = actual_lead_time.iloc[-1] if len(actual_lead_time) else 1
    demand_std_dev = actual_demand.std(ddof=0)
    safety_stock = demand_std_dev
    recommended_rop = max(0, round((end_lead_time * average_monthly_demand) + safety_stock))
    eoq = int(df["EOQ"].iloc[-1]) if "EOQ" in df.columns else 0
    stock_max = recommended_rop + eoq
    return {
        "average_monthly_demand": average_monthly_demand,
        "end_lead_time": end_lead_time,
        "demand_std_dev": demand_std_dev,
        "safety_stock": safety_stock,
        "recommended_rop": recommended_rop,
        "eoq": eoq,
        "stock_max": stock_max,
    }


def results_submission_configured():
    return (
        BIGQUERY_SCRIPT_URL
        and BIGQUERY_SCRIPT_URL != BIGQUERY_SCRIPT_URL_PLACEHOLDER
        and BIGQUERY_SCRIPT_URL.startswith("http")
    )


def get_lead_time_alert(month, lead_time_mode=None):
    if (lead_time_mode or current_lead_time_mode()) == "constant":
        return None
    strategy = current_cost_strategy()
    mitigation_note = ""
    if strategy == "supplier_agreement":
        mitigation_note = " Supplier agreement keeps your effective replenishment lead time at 1 month."
    elif strategy == "air_freight":
        mitigation_note = " Air freight applies only during this shock and makes replenishment arrive next month, not instantly."
    if month == cfg.shock_month:
        return {
            "kind": "increase",
            "title": "Lead time increased!",
            "message": f"Market lead time: {cfg.initial_lead_time} -> {cfg.shocked_lead_time} months.{mitigation_note}"
        }
    if month == cfg.full_recovery_month:
        return {
            "kind": "decrease",
            "title": "Lead time recovered!",
            "message": f"Market lead time: {cfg.shocked_lead_time} -> {cfg.recovered_lead_time} month.{mitigation_note}"
        }
    return None


def grouped_icons_html(qty, icon="📦", group_size=5, max_icons=10):
    if qty <= 0:
        return "—"
    n = max(1, min(max_icons, round(qty / group_size)))
    return " ".join([icon] * n)


def render_node_html(title, subtitle, qty, icon, border_color):
    icons = grouped_icons_html(qty, icon=icon)
    return f"""
        <div class="node" style="
            border: 2px solid {border_color};
            border-radius: 18px;
            padding: 14px;
            min-height: 180px;
            text-align: center;
            background: linear-gradient(180deg, rgba(15,20,32,0.96), rgba(10,14,26,0.96));
            position: relative;
            z-index: 2;
            box-shadow: 0 8px 28px rgba(0,0,0,0.35);
        ">
            <div style="font-size: 1.9rem; font-weight: 800; margin-bottom: 4px; color: #ffffff;">{title}</div>
            <div style="color: #ffffff; font-size: 0.88rem; margin-bottom: 12px;">{subtitle}</div>
            <div style="font-size: 1.8rem; min-height: 60px; line-height: 1.55;">{icons}</div>
            <div style="font-size: 2.15rem; font-weight: 900; margin-top: 10px; color: #ffffff;">{qty}</div>
        </div>
    """


def render_inventory_block_html(available_to_serve_qty, ending_on_hand_qty, inventory_position_qty, border_color="#1fd0c1"):
    on_hand_qty = ending_on_hand_qty
    on_hand_icons = grouped_icons_html(on_hand_qty, icon="🔩")
    position_icons = grouped_icons_html(inventory_position_qty, icon="📍")
    return f"""
        <div class="node" style="
            border: 2px solid {border_color};
            border-radius: 18px;
            padding: 14px;
            min-height: 220px;
            text-align: center;
            background: linear-gradient(180deg, rgba(15,20,32,0.96), rgba(10,14,26,0.96));
            position: relative;
            z-index: 2;
            box-shadow: 0 8px 28px rgba(0,0,0,0.35);
        ">
            <div style="font-size: 1.9rem; font-weight: 800; margin-bottom: 4px; color: #ffffff;">🏭 Warehouse</div>
            <div style="color: #ffffff; font-size: 0.88rem; margin-bottom: 12px;">One block, two planning views</div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <div style="border:1px solid rgba(255,255,255,0.12); border-radius:14px; padding:10px; background:rgba(255,255,255,0.06);">
                    <div style="font-size:0.78rem; color:#ffffff; font-weight:700;">Inventory On Hand</div>
                    <div style="font-size:1.45rem; min-height:46px; line-height:1.4; margin-top:6px;">{on_hand_icons}</div>
                    <div style="font-size:2rem; font-weight:900; margin-top:6px; color:#ffffff;">{on_hand_qty}</div>
                </div>
                <div style="border:1px solid rgba(255,255,255,0.12); border-radius:14px; padding:10px; background:rgba(255,255,255,0.06);">
                    <div style="font-size:0.78rem; color:#ffffff; font-weight:700;">Inventory Position</div>
                    <div style="font-size:1.45rem; min-height:46px; line-height:1.4; margin-top:6px;">{position_icons}</div>
                    <div style="font-size:2rem; font-weight:900; margin-top:6px; color:#ffffff;">{inventory_position_qty}</div>
                </div>
            </div>
        </div>
    """


def render_inventory_timing_block_html(available_to_serve_qty, ending_on_hand_qty, inventory_position_qty, border_color="#1fd0c1"):
    available_icons = grouped_icons_html(available_to_serve_qty, icon="o")
    ending_icons = grouped_icons_html(ending_on_hand_qty, icon="o")
    position_icons = grouped_icons_html(inventory_position_qty, icon=".")
    return f"""
        <div class="node" style="
            border: 2px solid {border_color};
            border-radius: 18px;
            padding: 14px;
            min-height: 220px;
            text-align: center;
            background: linear-gradient(180deg, rgba(15,20,32,0.96), rgba(10,14,26,0.96));
            position: relative;
            z-index: 2;
            box-shadow: 0 8px 28px rgba(0,0,0,0.35);
        ">
            <div style="font-size: 1.9rem; font-weight: 800; margin-bottom: 4px; color: #ffffff;">Warehouse</div>
            <div style="color: #ffffff; font-size: 0.88rem; margin-bottom: 12px;">Receive first, serve demand, then reorder</div>

            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px;">
                <div style="border:1px solid rgba(255,255,255,0.12); border-radius:14px; padding:10px; background:rgba(255,255,255,0.06);">
                    <div style="font-size:0.78rem; color:#ffffff; font-weight:700;">Available Before Demand</div>
                    <div style="font-size:1.45rem; min-height:46px; line-height:1.4; margin-top:6px;">{available_icons}</div>
                    <div style="font-size:2rem; font-weight:900; margin-top:6px; color:#ffffff;">{available_to_serve_qty}</div>
                </div>
                <div style="border:1px solid rgba(255,255,255,0.12); border-radius:14px; padding:10px; background:rgba(255,255,255,0.06);">
                    <div style="font-size:0.78rem; color:#ffffff; font-weight:700;">Ending On Hand</div>
                    <div style="font-size:1.45rem; min-height:46px; line-height:1.4; margin-top:6px;">{ending_icons}</div>
                    <div style="font-size:2rem; font-weight:900; margin-top:6px; color:#ffffff;">{ending_on_hand_qty}</div>
                </div>
                <div style="border:1px solid rgba(255,255,255,0.12); border-radius:14px; padding:10px; background:rgba(255,255,255,0.06);">
                    <div style="font-size:0.78rem; color:#ffffff; font-weight:700;">Position After Order</div>
                    <div style="font-size:1.45rem; min-height:46px; line-height:1.4; margin-top:6px;">{position_icons}</div>
                    <div style="font-size:2rem; font-weight:900; margin-top:6px; color:#ffffff;">{inventory_position_qty}</div>
                </div>
            </div>
        </div>
    """


def build_combined_demand_svg(item_name, compact=False):
    """
    Combined demand chart:
    - Always starts with historical demand for Jan-Dec 2025.
    - Reveals actual game demand only for months already played.
    - Continues updating after Dec 2026 into 2027.
    - If the chart becomes crowded, it removes the oldest historical months first.
    """
    historical_2025 = cfg.item_last_year_demand[item_name]
    played_months = min(len(st.session_state.history), cfg.months)
    if item_name == st.session_state.get("selected_item") and "game_demand" in st.session_state:
        actual_game_demand = st.session_state.game_demand[:played_months]
    else:
        actual_game_demand = [cfg.demand(m, item_name) for m in range(1, played_months + 1)]

    labels_2025 = [f"{m}25" for m in MONTH_NAMES_12]

    # Build labels for all revealed game months: Jan26-Dec26, then Jan27-Aug27.
    labels_game = []
    for month_number in range(1, played_months + 1):
        full_label = get_game_month_label(month_number)  # example: Jan 2026
        month_short, year_full = full_label.split()
        labels_game.append(f"{month_short}{year_full[-2:]}")

    values = historical_2025 + actual_game_demand
    labels = labels_2025 + labels_game
    groups = (["hist"] * len(historical_2025)) + (["actual"] * len(actual_game_demand))

    # Keep the chart readable. Once many 2026/2027 months are revealed,
    # remove the oldest historical months from the beginning.
    max_visible_bars = 24
    hidden_old_bars = 0
    if len(values) > max_visible_bars:
        hidden_old_bars = len(values) - max_visible_bars
        values = values[hidden_old_bars:]
        labels = labels[hidden_old_bars:]
        groups = groups[hidden_old_bars:]

    if compact:
        chart_width = 720
        chart_height = 210
        title_size = "0.90rem"
        subtitle_size = "0.68rem"
    else:
        chart_width = 920
        chart_height = 205
        title_size = "0.90rem"
        subtitle_size = "0.70rem"

    left_pad = 28
    right_pad = 18
    top_pad = 34
    bottom_pad = 54
    usable_width = chart_width - left_pad - right_pad
    usable_height = chart_height - top_pad - bottom_pad

    max_val = max(values) if values and max(values) > 0 else 1
    bar_count = max(len(values), 1)
    slot_width = usable_width / bar_count
    bar_width = max(8, slot_width * 0.55)

    svg_parts = []

    # Grid lines
    for i in range(5):
        y = top_pad + (usable_height / 4) * i
        svg_parts.append(
            f'<line x1="{left_pad}" y1="{y:.1f}" x2="{chart_width-right_pad}" y2="{y:.1f}" '
            f'stroke="rgba(255,255,255,0.08)" stroke-width="1" />'
        )

    # Separator between historical and actual, if both are visible.
    hist_visible_count = groups.count("hist")
    actual_visible_count = groups.count("actual")
    if hist_visible_count > 0 and actual_visible_count > 0:
        separator_x = left_pad + hist_visible_count * slot_width
        svg_parts.append(
            f'<line x1="{separator_x:.1f}" y1="{top_pad-8}" x2="{separator_x:.1f}" y2="{top_pad+usable_height+10}" '
            f'stroke="rgba(255,255,255,0.25)" stroke-width="2" stroke-dasharray="5,5" />'
        )

    # Latest actual month in the visible chart.
    latest_actual_indices = [i for i, g in enumerate(groups) if g == "actual"]
    latest_actual_index = latest_actual_indices[-1] if latest_actual_indices else None

    for i, (val, label, group) in enumerate(zip(values, labels, groups)):
        x = left_pad + i * slot_width + (slot_width - bar_width) / 2
        h = (val / max_val) * usable_height if max_val else 0
        y = top_pad + usable_height - h

        if group == "hist":
            fill = "#6a7bd1"
            opacity = "0.72"
        else:
            fill = "#45d0c5"
            opacity = "1.0"

        is_latest_actual = latest_actual_index is not None and i == latest_actual_index
        stroke = "#ffdf6b" if is_latest_actual else "none"
        stroke_width = "4" if is_latest_actual else "0"

        svg_parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{h:.1f}" '
            f'rx="6" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" />'
        )

        svg_parts.append(
            f'<text x="{x + bar_width/2:.1f}" y="{max(y - 6, 14):.1f}" text-anchor="middle" '
            f'font-size="8.5" fill="white">{val}</text>'
        )

        svg_parts.append(
            f'<text x="{x + bar_width/2:.1f}" y="{chart_height - 14}" text-anchor="middle" '
            f'font-size="7.8" fill="white">{label}</text>'
        )

    trim_note = ""
    if hidden_old_bars > 0:
        trim_note = f" Oldest historical months hidden: {hidden_old_bars}."

    subtitle_text = (
        "Historical 2025 demand is visible first. Each play reveals only the next actual game month."
        + trim_note
    )

    return f"""
    <div style="
        margin-bottom:8px;
        border:1px solid rgba(255,255,255,0.10);
        border-radius:14px;
        padding:7px 10px;
        background:rgba(255,255,255,0.05);
    ">
        <div style="font-size:{title_size}; font-weight:800; color:white; margin-bottom:4px;">
            Demand Timeline
        </div>
        <div style="font-size:{subtitle_size}; color:#d8def7; margin-bottom:5px;">
            {subtitle_text}
        </div>
        <div style="font-size:0.70rem; color:#ffffff; margin-bottom:2px;">
            <span style="color:#cbd5ff;">■</span> 2025 history &nbsp;&nbsp; <span style="color:#bffaf4;">■</span> revealed game demand
        </div>
        <svg width="100%" viewBox="0 0 {chart_width} {chart_height}" preserveAspectRatio="xMidYMid meet">
            {''.join(svg_parts)}
        </svg>
    </div>
    """


def build_inventory_position_rop_svg():
    """
    Small compact chart for played months only.
    Inventory Position = bars.
    ROP = yellow line.
    This is intentionally small so it does not block the main animation blocks.
    """
    if not st.session_state.history:
        return ""

    df = pd.DataFrame(st.session_state.history)

    labels = []
    for month_number in df["Month"].tolist():
        full_label = get_game_month_label(month_number)
        month_short, year_full = full_label.split()
        labels.append(f"{month_short}{year_full[-2:]}")

    inv_values = df["Inventory Position After Order"].tolist()
    rop_values = df["ROP Used"].tolist()

    # Show only latest months to keep the chart compact.
    max_visible_points = 8
    if len(labels) > max_visible_points:
        labels = labels[-max_visible_points:]
        inv_values = inv_values[-max_visible_points:]
        rop_values = rop_values[-max_visible_points:]

    chart_width = 980
    chart_height = 120
    left_pad = 34
    right_pad = 24
    top_pad = 20
    bottom_pad = 28
    usable_width = chart_width - left_pad - right_pad
    usable_height = chart_height - top_pad - bottom_pad

    max_val = max(max(inv_values), max(rop_values), 1) * 1.2

    count = len(inv_values)
    slot_width = usable_width / max(count, 1)
    bar_width = max(8, min(38, slot_width * 0.42))

    svg_parts = []

    # Grid lines
    for i in range(3):
        y = top_pad + (usable_height / 2) * i
        svg_parts.append(
            f'<line x1="{left_pad}" y1="{y:.1f}" x2="{chart_width-right_pad}" y2="{y:.1f}" '
            f'stroke="rgba(255,255,255,0.07)" stroke-width="1" />'
        )

    points = []
    for i, (label, inv, rop) in enumerate(zip(labels, inv_values, rop_values)):
        x_center = left_pad + i * slot_width + slot_width / 2
        bar_x = x_center - bar_width / 2
        bar_h = (inv / max_val) * usable_height if max_val else 0
        bar_y = top_pad + usable_height - bar_h

        svg_parts.append(
            f'<rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_width:.1f}" height="{bar_h:.1f}" '
            f'rx="4" fill="#45d0c5" fill-opacity="0.85" />'
        )

        svg_parts.append(
            f'<text x="{x_center:.1f}" y="{max(bar_y - 4, 11):.1f}" text-anchor="middle" '
            f'font-size="8.5" fill="white">{inv}</text>'
        )

        rop_y = top_pad + usable_height - ((rop / max_val) * usable_height if max_val else 0)
        points.append((x_center, rop_y, rop))

        svg_parts.append(
            f'<text x="{x_center:.1f}" y="{chart_height - 8}" text-anchor="middle" '
            f'font-size="8.5" fill="white">{label}</text>'
        )

    # ROP line
    if len(points) == 1:
        x, y, rop = points[0]
        svg_parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#ffdf6b" />')
        svg_parts.append(
            f'<text x="{x:.1f}" y="{max(y - 7, 11):.1f}" text-anchor="middle" font-size="8.5" fill="#ffdf6b">ROP {rop}</text>'
        )
    else:
        line_points = " ".join([f"{x:.1f},{y:.1f}" for x, y, _ in points])
        svg_parts.append(
            f'<polyline points="{line_points}" fill="none" stroke="#ffdf6b" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round" />'
        )
        for x, y, _ in points:
            svg_parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#ffdf6b" />')

    return f"""
    <div style="
        margin-top:10px;
        border:1px solid rgba(255,255,255,0.08);
        border-radius:12px;
        padding:8px 10px;
        background:rgba(255,255,255,0.035);
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
            <div style="font-size:0.88rem; font-weight:800; color:white;">
                Inventory Position vs ROP
            </div>
            <div style="font-size:0.70rem; color:#ffffff;">
                <span style="color:#bffaf4;">■</span> Inventory Position &nbsp;
                <span style="color:#ffdf6b;">●</span> ROP
            </div>
        </div>
        <svg width="100%" viewBox="0 0 {chart_width} {chart_height}" preserveAspectRatio="xMidYMid meet">
            {''.join(svg_parts)}
        </svg>
    </div>
    """


def submit_result_to_bigquery_endpoint(payload):
    response = requests.post(
        BIGQUERY_SCRIPT_URL,
        json=payload,
        timeout=10
    )
    return response


# =========================================================
# SECTION 5: GAME LOGIC
# =========================================================

def run_month(player_rop):
    month = st.session_state.month
    lead_time = cfg.lead_time(month, current_lead_time_mode())
    effective_lead_time = effective_lead_time_for_strategy(lead_time, current_cost_strategy())
    item_name = st.session_state.selected_item

    # 1. Receive open orders that arrive this month.
    incoming = sum(x["qty"] for x in st.session_state.pipeline if x["arrival"] == month)
    st.session_state.pipeline = [x for x in st.session_state.pipeline if x["arrival"] != month]

    # 2. Demand happens and backlog from earlier months must also be served.
    if "game_demand" in st.session_state and month <= len(st.session_state.game_demand):
        new_demand = st.session_state.game_demand[month - 1]
    else:
        new_demand = cfg.demand(month, item_name)
    backlog_before = st.session_state.backlog
    total_customer_need = new_demand + backlog_before

    starting_inventory = st.session_state.inventory
    inventory_after_incoming = starting_inventory + incoming

    fulfilled = min(inventory_after_incoming, total_customer_need)
    ending_inventory = inventory_after_incoming - fulfilled
    ending_backlog = total_customer_need - fulfilled
    air_freight_units = 0
    air_freight_cost = 0.0

    backlog_this_period = max(0, new_demand - min(inventory_after_incoming, new_demand))

    # 3. Update inventory and backlog before checking reorder logic.
    st.session_state.inventory = ending_inventory
    st.session_state.backlog = ending_backlog

    # Corrected inventory position after current demand is processed.
    # This is the value used to decide whether an order-up-to order should be triggered.
    inventory_position_before_order = ending_inventory + pipeline_total() - ending_backlog

    # 4. Automatic reorder logic.
    # If Inventory Position <= ROP, order up to Stock Max.
    # Stock Max = ROP + EOQ. Order Qty = Stock Max - Inventory Position.
    auto_order_qty = 0
    auto_order_arrival = None
    item_eoq = cfg.get_item_eoq(item_name)
    stock_max = player_rop + item_eoq
    reorder_triggered = inventory_position_before_order <= player_rop

    if reorder_triggered:
        auto_order_qty = max(0, stock_max - inventory_position_before_order)
        if current_cost_strategy() == "air_freight" and lead_time > 1:
            air_freight_units = auto_order_qty
            air_freight_cost = air_freight_units * cfg.air_freight_cost_per_unit
        auto_order_arrival = month + effective_lead_time
        st.session_state.pipeline.append({
            "arrival": auto_order_arrival,
            "qty": auto_order_qty
        })

    inventory_position_after_order = ending_inventory + pipeline_total() - ending_backlog
    current_pipeline = pipeline_total()

    # 5. Cost calculation.
    inventory_holding_cost = ending_inventory * cfg.holding_cost_per_unit
    backlog_cost = ending_backlog * cfg.backlog_cost_per_unit
    supplier_agreement_cost = (
        cfg.supplier_agreement_monthly_fee
        if current_cost_strategy() == "supplier_agreement"
        else 0.0
    )
    month_total_cost = inventory_holding_cost + backlog_cost + supplier_agreement_cost + air_freight_cost

    st.session_state.cumulative_cost += month_total_cost

    row = {
        "Month": month,
        "Calendar Month": get_game_month_label(month),
        "Item": item_name,
        "Lead Time": lead_time,
        "Effective Lead Time": effective_lead_time,
        "ROP Used": player_rop,
        "EOQ": item_eoq,
        "Stock Max": stock_max,
        "Starting Inventory": starting_inventory,
        "Incoming Purchases": incoming,
        "Inventory After Incoming": inventory_after_incoming,
        "New Demand": new_demand,
        "Backlog From Previous Month": backlog_before,
        "Total Customer Need": total_customer_need,
        "Fulfilled": fulfilled,
        "Backlog This Period": backlog_this_period,
        "Ending Backlog": ending_backlog,
        "Ending Inventory": ending_inventory,
        "Inventory Position Before Order": inventory_position_before_order,
        "Inventory Position Formula": "Ending Inventory + Pipeline - Ending Backlog",
        "Order Rule": "If Inventory Position <= ROP, order up to Stock Max (ROP + EOQ)",
        "Reorder Triggered": "Yes" if reorder_triggered else "No",
        "PO Placed": auto_order_qty,
        "PO Arrival Month": get_game_month_label(auto_order_arrival) if auto_order_arrival is not None and auto_order_arrival <= cfg.months else auto_order_arrival if auto_order_arrival is not None else "",
        "Pipeline": current_pipeline,
        "Inventory Position After Order": inventory_position_after_order,
        "Inventory Holding Cost": round(inventory_holding_cost, 2),
        "Backlog Cost": round(backlog_cost, 2),
        "Supplier Agreement Cost": round(supplier_agreement_cost, 2),
        "Air Freight Units": air_freight_units,
        "Air Freight Cost": round(air_freight_cost, 2),
        "Month Total Cost": round(month_total_cost, 2),
        "Cumulative Total Cost": round(st.session_state.cumulative_cost, 2),
    }

    st.session_state.history.append(row)
    st.session_state.current_rop = player_rop
    st.session_state.month += 1

    return row


def simulate_fixed_rop_policy(item_name, lead_time_mode, fixed_rop, cost_strategy="none", demand_series=None):
    inventory = cfg.get_item_initial_inventory(item_name)
    pipeline = []
    backlog = 0
    cumulative_cost = 0.0
    rows = []

    for month in range(1, cfg.months + 1):
        lead_time = cfg.lead_time(month, lead_time_mode)
        effective_lead_time_for_month = effective_lead_time_for_strategy(lead_time, cost_strategy)
        incoming = sum(x["qty"] for x in pipeline if x["arrival"] == month)
        pipeline = [x for x in pipeline if x["arrival"] != month]

        if demand_series is not None and month <= len(demand_series):
            new_demand = demand_series[month - 1]
        else:
            new_demand = cfg.demand(month, item_name)
        backlog_before = backlog
        total_customer_need = new_demand + backlog_before
        inventory_after_incoming = inventory + incoming
        fulfilled = min(inventory_after_incoming, total_customer_need)
        ending_inventory = inventory_after_incoming - fulfilled
        ending_backlog = total_customer_need - fulfilled
        air_freight_units = 0
        air_freight_cost = 0.0
        inventory_position_before_order = ending_inventory + sum(x["qty"] for x in pipeline) - ending_backlog

        item_eoq = cfg.get_item_eoq(item_name)
        stock_max = fixed_rop + item_eoq

        if inventory_position_before_order <= fixed_rop:
            order_qty = max(0, stock_max - inventory_position_before_order)
            if cost_strategy == "air_freight" and lead_time > 1:
                air_freight_units = order_qty
                air_freight_cost = air_freight_units * cfg.air_freight_cost_per_unit
            pipeline.append({
                "arrival": month + effective_lead_time_for_month,
                "qty": order_qty,
            })

        inventory = ending_inventory
        backlog = ending_backlog
        pipeline_qty = sum(x["qty"] for x in pipeline)
        inventory_position_after_order = inventory + pipeline_qty - backlog
        inventory_holding_cost = inventory * cfg.holding_cost_per_unit
        backlog_cost = backlog * cfg.backlog_cost_per_unit
        supplier_agreement_cost = (
            cfg.supplier_agreement_monthly_fee
            if cost_strategy == "supplier_agreement"
            else 0.0
        )
        month_total_cost = inventory_holding_cost + backlog_cost + supplier_agreement_cost + air_freight_cost
        cumulative_cost += month_total_cost

        rows.append({
            "Month": month,
            "Calendar Month": get_game_month_label(month),
            "Policy": f"Baseline ROP {fixed_rop}",
            "ROP Used": fixed_rop,
            "Stock Max": stock_max,
            "Lead Time": lead_time,
            "Effective Lead Time": effective_lead_time_for_month,
            "New Demand": new_demand,
            "Total Customer Need": total_customer_need,
            "Fulfilled": fulfilled,
            "Ending Inventory": ending_inventory,
            "Ending Backlog": ending_backlog,
            "Pipeline": pipeline_qty,
            "Inventory Position After Order": inventory_position_after_order,
            "Inventory Holding Cost": round(inventory_holding_cost, 2),
            "Backlog Cost": round(backlog_cost, 2),
            "Supplier Agreement Cost": round(supplier_agreement_cost, 2),
            "Air Freight Units": air_freight_units,
            "Air Freight Cost": round(air_freight_cost, 2),
            "Month Total Cost": round(month_total_cost, 2),
            "Cumulative Total Cost": round(cumulative_cost, 2),
        })

    return pd.DataFrame(rows)


def summarize_performance(df, label):
    total_need = df["Total Customer Need"].sum()
    total_fulfilled = df["Fulfilled"].sum()
    fill_rate = (total_fulfilled / total_need) * 100 if total_need > 0 else 0
    final_ending_inventory = df["Ending Inventory"].iloc[-1]
    benchmark = calculate_actual_stockmax_benchmark(df)
    final_stock_max = benchmark["stock_max"]
    total_cost = round(df["Month Total Cost"].sum(), 0)
    cost_points = total_cost
    fill_rate_gap = max(0, TARGET_FILL_RATE_PERCENT - fill_rate)
    fill_rate_penalty = round(fill_rate_gap * FILL_RATE_PENALTY_PER_PERCENT, 0)
    excess_inventory_units = max(0, final_ending_inventory - final_stock_max)
    overstock_penalty = round(excess_inventory_units * OVERSTOCK_PENALTY_PER_UNIT, 0)
    total_penalty = cost_points + fill_rate_penalty + overstock_penalty
    return {
        "Policy": label,
        "Average Stock": round(df["Ending Inventory"].mean(), 1),
        "Average Pipeline": round(df["Pipeline"].mean(), 1),
        "Ending Inventory": round(final_ending_inventory, 0),
        "Final Stock Max": round(final_stock_max, 0),
        "Actual Average Monthly Demand": round(benchmark["average_monthly_demand"], 1),
        "Actual End Lead Time": round(benchmark["end_lead_time"], 1),
        "Actual Demand Std Dev": round(benchmark["demand_std_dev"], 1),
        "Actual Safety Stock": round(benchmark["safety_stock"], 1),
        "Actual ROP 85": round(benchmark["recommended_rop"], 0),
        "Inventory Cost": round(df["Inventory Holding Cost"].sum(), 0),
        "Backlog Cost": round(df["Backlog Cost"].sum(), 0),
        "Supplier Agreement Cost": round(df.get("Supplier Agreement Cost", pd.Series([0])).sum(), 0),
        "Air Freight Cost": round(df.get("Air Freight Cost", pd.Series([0])).sum(), 0),
        "Total Cost": total_cost,
        "Cost Points": cost_points,
        "Fill Rate": round(fill_rate, 1),
        "Fill Rate Penalty": fill_rate_penalty,
        "Excess Inventory Units": round(excess_inventory_units, 0),
        "Overstock Penalty": overstock_penalty,
        "Total Penalty": total_penalty,
    }


def build_performance_report(player_history, item_name, lead_time_mode, cost_strategy="none"):
    player_df = pd.DataFrame(player_history).copy()
    player_df["Policy"] = "Player"
    demand_series = player_df["New Demand"].tolist()
    baseline_4_df = simulate_fixed_rop_policy(item_name, lead_time_mode, 4, cost_strategy, demand_series)
    baseline_12_df = simulate_fixed_rop_policy(item_name, lead_time_mode, 12, cost_strategy, demand_series)

    summary = pd.DataFrame([
        summarize_performance(player_df, "Player"),
        summarize_performance(baseline_4_df, "Baseline ROP 4"),
        summarize_performance(baseline_12_df, "Baseline ROP 12"),
    ])

    trend_df = pd.concat([
        player_df[["Month", "Policy", "Ending Inventory", "Pipeline", "Ending Backlog", "Cumulative Total Cost"]],
        baseline_4_df[["Month", "Policy", "Ending Inventory", "Pipeline", "Ending Backlog", "Cumulative Total Cost"]],
        baseline_12_df[["Month", "Policy", "Ending Inventory", "Pipeline", "Ending Backlog", "Cumulative Total Cost"]],
    ], ignore_index=True)

    return summary, trend_df


def render_scorecards(summary):
    cards = []
    for row in summary.to_dict("records"):
        player_class = " player" if row["Policy"] == "Player" else ""
        cards.append(
            f'<div class="scorecard{player_class}">'
            f'<div class="scorecard-policy">{row["Policy"]}</div>'
            f'<div class="scorecard-row"><span>Penalty Points</span><strong>{row["Total Penalty"]:,.0f}</strong></div>'
            f'<div class="scorecard-row"><span>Total Cost</span><strong>{row["Total Cost"]:,.0f}</strong></div>'
            f'<div class="scorecard-row"><span>Fill Rate</span><strong>{row["Fill Rate"]:.1f}%</strong></div>'
            f'<div class="scorecard-row"><span>Ending Stock</span><strong>{row["Ending Inventory"]:,.0f}</strong></div>'
            f'<div class="scorecard-row"><span>Avg Stock</span><strong>{row["Average Stock"]:.1f}</strong></div>'
            f'<div class="scorecard-row"><span>Avg Pipeline</span><strong>{row["Average Pipeline"]:.1f}</strong></div>'
            f'</div>'
        )

    return f'<div class="scorecard-grid">{"".join(cards)}</div>'


def render_penalty_overview(summary, variant_index, completed_reports):
    cards = []
    if variant_index == 0:
        rows = summary.to_dict("records")
        best_penalty = min(row["Total Penalty"] for row in rows)
        for row in rows:
            is_player = row["Policy"] == "Player"
            gap = row["Total Penalty"] - best_penalty
            note = "Best penalty score in this comparison." if gap == 0 else f"{gap:,.0f} points above the best score."
            cards.append(
                f'<div class="penalty-card{" player" if is_player else ""}">'
                f'<div class="penalty-card-title">{row["Policy"]}</div>'
                f'<div class="penalty-card-value">{row["Total Penalty"]:,.0f}</div>'
                f'<div class="penalty-card-note">Penalty points = total cost + penalties.</div>'
                f'<div class="penalty-card-note">{note}</div>'
                f'</div>'
            )
        title = "Penalty comparison: player vs ROP baselines"
    else:
        current = summary[summary["Policy"] == "Player"].iloc[0].to_dict()
        round_1 = completed_reports[0] if completed_reports else None
        rows = []
        if round_1:
            rows.append(round_1)
        rows.append(current | {"Round": "Round 2", "Scenario": "Current round"})
        best_penalty = min(row["Total Penalty"] for row in rows)
        for row in rows:
            label = row.get("Round", row.get("Policy", "Round"))
            is_player = label == "Round 2"
            gap = row["Total Penalty"] - best_penalty
            note = "Best penalty score between your two rounds." if gap == 0 else f"{gap:,.0f} points above your best round."
            cards.append(
                f'<div class="penalty-card{" player" if is_player else ""}">'
                f'<div class="penalty-card-title">{label}</div>'
                f'<div class="penalty-card-value">{row["Total Penalty"]:,.0f}</div>'
                f'<div class="penalty-card-note">{row.get("Scenario", "")}</div>'
                f'<div class="penalty-card-note">{note}</div>'
                f'</div>'
            )
        title = "Penalty comparison: Round 1 vs Round 2"

    return (
        '<div class="chart-panel">'
        f'<div class="chart-title">{title}</div>'
        '<div class="penalty-overview-grid">'
        f'{"".join(cards)}'
        '</div>'
        '</div>'
    )


def build_round_complete_feedback(summary, variant_index, completed_reports):
    player = summary[summary["Policy"] == "Player"].iloc[0].to_dict()
    lines = []

    if player["Fill Rate"] < TARGET_FILL_RATE_PERCENT:
        gap = TARGET_FILL_RATE_PERCENT - player["Fill Rate"]
        lines.append(f"You did not achieve the target fill rate of {TARGET_FILL_RATE_PERCENT:.0f}%. You were {gap:.1f} percentage points below target.")
    else:
        lines.append(f"You achieved the target fill rate of {TARGET_FILL_RATE_PERCENT:.0f}% with {player['Fill Rate']:.1f}%.")

    if player["Overstock Penalty"] > 0:
        lines.append(f"Ending stock was above the calculated Stock Max, adding {player['Overstock Penalty']:,.0f} overstock penalty points.")
    elif player["Inventory Cost"] > player["Backlog Cost"] and player["Fill Rate"] >= TARGET_FILL_RATE_PERCENT:
        lines.append("You protected service, but inventory cost became the main cost driver. That is the classic service-versus-stock trade-off.")
    elif player["Backlog Cost"] > 0:
        lines.append(f"Backlog cost was {player['Backlog Cost']:,.0f}, meaning shortages still hurt the score.")
    else:
        lines.append("Backlog was controlled well in this round.")

    if variant_index == 0:
        baseline_rows = summary[summary["Policy"] != "Player"]
        best_baseline = baseline_rows.loc[baseline_rows["Total Penalty"].idxmin()].to_dict()
        player_gap = player["Total Penalty"] - best_baseline["Total Penalty"]
        if player_gap <= 0:
            lines.append(f"Your penalty points were {abs(player_gap):,.0f} better than the best fixed baseline ({best_baseline['Policy']}).")
        else:
            lines.append(f"Your penalty points were {player_gap:,.0f} higher than the best fixed baseline ({best_baseline['Policy']}).")
        lines.append(
            "Penalty comparison: "
            f"Player {player['Total Penalty']:,.0f}, "
            f"ROP 4 {summary.loc[summary['Policy'] == 'Baseline ROP 4', 'Total Penalty'].iloc[0]:,.0f}, "
            f"ROP 12 {summary.loc[summary['Policy'] == 'Baseline ROP 12', 'Total Penalty'].iloc[0]:,.0f}."
        )
    elif completed_reports:
        round_1 = completed_reports[0]
        delta = player["Total Penalty"] - round_1["Total Penalty"]
        if delta < 0:
            lines.append(f"Round 2 improved your penalty score by {abs(delta):,.0f} points compared with round 1.")
        elif delta > 0:
            lines.append(f"Round 2 added {delta:,.0f} more penalty points than round 1.")
        else:
            lines.append("Round 2 matched your round 1 penalty score.")
        lines.append(f"Round 1 penalty points: {round_1['Total Penalty']:,.0f}. Round 2 penalty points: {player['Total Penalty']:,.0f}.")

    return lines


def render_report_table(summary):
    headers = [
        "Policy",
        "Average Stock",
        "Average Pipeline",
        "Inventory Cost",
        "Backlog Cost",
        "Agreement Cost",
        "Air Freight Cost",
        "Total Cost",
        "Cost Points",
        "Fill Rate",
        "Fill Rate Penalty",
        "Actual End Lead Time",
        "Actual ROP 85",
        "Actual Stock Max",
        "Excess Inventory",
        "Overstock Penalty",
        "Penalty Points",
    ]
    max_total_cost = summary["Total Cost"].max()
    rows = []

    for row in summary.to_dict("records"):
        policy_class = " policy-player" if row["Policy"] == "Player" else ""
        total_cost_class = " cost-high" if row["Total Cost"] == max_total_cost else ""
        fill_class = " fill-good" if row["Fill Rate"] >= TARGET_FILL_RATE_PERCENT else " fill-low"
        rows.append(
            "<tr>"
            f'<td class="{policy_class.strip()}">{row["Policy"]}</td>'
            f'<td class="number">{row["Average Stock"]:.1f}</td>'
            f'<td class="number">{row["Average Pipeline"]:.1f}</td>'
            f'<td class="number">{row["Inventory Cost"]:,.0f}</td>'
            f'<td class="number">{row["Backlog Cost"]:,.0f}</td>'
            f'<td class="number">{row["Supplier Agreement Cost"]:,.0f}</td>'
            f'<td class="number">{row["Air Freight Cost"]:,.0f}</td>'
            f'<td class="number{total_cost_class}">{row["Total Cost"]:,.0f}</td>'
            f'<td class="number">{row["Cost Points"]:,.0f}</td>'
            f'<td class="number{fill_class}">{row["Fill Rate"]:.1f}%</td>'
            f'<td class="number">{row["Fill Rate Penalty"]:,.0f}</td>'
            f'<td class="number">{row["Actual End Lead Time"]:.1f}</td>'
            f'<td class="number">{row["Actual ROP 85"]:,.0f}</td>'
            f'<td class="number">{row["Final Stock Max"]:,.0f}</td>'
            f'<td class="number">{row["Excess Inventory Units"]:,.0f}</td>'
            f'<td class="number">{row["Overstock Penalty"]:,.0f}</td>'
            f'<td class="number">{row["Total Penalty"]:,.0f}</td>'
            "</tr>"
        )

    header_html = "".join(f"<th>{header}</th>" for header in headers)
    return f'<table class="report-table"><thead><tr>{header_html}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def build_email_report_html(summary, player_name, player_email, scenario_title, item_name, lead_time_mode):
    safe_player = html_escape(player_name)
    safe_email = html_escape(player_email)
    safe_scenario = html_escape(scenario_title)
    safe_item = html_escape(item_name)
    safe_lead_time_mode = html_escape(lead_time_mode)

    cards = []
    for row in summary.to_dict("records"):
        border_color = "#facc15" if row["Policy"] == "Player" else "#93c5fd"
        cards.append(f"""
        <td style="width:33.33%; padding:8px; vertical-align:top;">
            <div style="border:1px solid {border_color}; border-radius:14px; padding:14px; background:#111827; color:#f9fafb;">
                <div style="font-size:16px; font-weight:800; margin-bottom:8px;">{html_escape(row["Policy"])}</div>
                <div>Total Cost: <strong>{row["Total Cost"]:,.0f}</strong></div>
                <div>Penalty Points: <strong>{row["Total Penalty"]:,.0f}</strong></div>
                <div>Fill Rate: <strong>{row["Fill Rate"]:.1f}%</strong></div>
                <div>End Lead Time: <strong>{row["Actual End Lead Time"]:.1f} month(s)</strong></div>
                <div>Actual Stock Max: <strong>{row["Final Stock Max"]:,.0f}</strong></div>
                <div>Average Stock: <strong>{row["Average Stock"]:.1f}</strong></div>
                <div>Average Pipeline: <strong>{row["Average Pipeline"]:.1f}</strong></div>
            </div>
        </td>
        """)

    max_cost = max(summary["Inventory Cost"].max(), summary["Backlog Cost"].max(), 1)
    table_rows = []
    for row in summary.to_dict("records"):
        inv_width = max(4, int((row["Inventory Cost"] / max_cost) * 100))
        backlog_width = max(4, int((row["Backlog Cost"] / max_cost) * 100)) if row["Backlog Cost"] > 0 else 0
        backlog_bar = (
            f'<div style="height:10px; width:{backlog_width}%; background:#2684ff; border-radius:8px;"></div>'
            if backlog_width
            else '<div style="height:10px; width:4%; background:#d1d5db; border-radius:8px;"></div>'
        )
        table_rows.append(f"""
        <tr>
            <td style="padding:10px; border-bottom:1px solid #e5e7eb;">{html_escape(row["Policy"])}</td>
            <td style="padding:10px; border-bottom:1px solid #e5e7eb; text-align:right;">{row["Inventory Cost"]:,.0f}</td>
            <td style="padding:10px; border-bottom:1px solid #e5e7eb;">
                <div style="height:10px; width:{inv_width}%; background:#ff3b3b; border-radius:8px;"></div>
            </td>
            <td style="padding:10px; border-bottom:1px solid #e5e7eb; text-align:right;">{row["Backlog Cost"]:,.0f}</td>
            <td style="padding:10px; border-bottom:1px solid #e5e7eb;">{backlog_bar}</td>
            <td style="padding:10px; border-bottom:1px solid #e5e7eb; text-align:right;">{row["Fill Rate"]:.1f}%</td>
            <td style="padding:10px; border-bottom:1px solid #e5e7eb; text-align:right;">{row["Total Penalty"]:,.0f}</td>
        </tr>
        """)

    return f"""
    <div style="font-family:Arial, sans-serif; color:#111827; max-width:900px;">
        <div style="background:#111827; color:#ffffff; padding:20px; border-radius:16px;">
            <div style="font-size:13px; color:#bffaf4; font-weight:800; text-transform:uppercase;">Inventory Game Report</div>
            <h2 style="margin:6px 0 8px;">{safe_scenario}</h2>
            <div>Player: <strong>{safe_player}</strong> ({safe_email})</div>
            <div>Item: <strong>{safe_item}</strong> | Lead-time mode: <strong>{safe_lead_time_mode}</strong></div>
        </div>
        <table role="presentation" style="width:100%; border-collapse:collapse; margin:14px 0;">
            <tr>{"".join(cards)}</tr>
        </table>
        <h3 style="margin-top:18px;">Cost and fill-rate comparison</h3>
        <table style="width:100%; border-collapse:collapse; border:1px solid #e5e7eb;">
            <thead>
                <tr style="background:#f3f4f6;">
                    <th style="padding:10px; text-align:left;">Policy</th>
                    <th style="padding:10px; text-align:right;">Inventory Cost</th>
                    <th style="padding:10px; text-align:left;">Inventory Cost Bar</th>
                    <th style="padding:10px; text-align:right;">Backlog Cost</th>
                    <th style="padding:10px; text-align:left;">Backlog Cost Bar</th>
                    <th style="padding:10px; text-align:right;">Fill Rate</th>
                    <th style="padding:10px; text-align:right;">Penalty Points</th>
                </tr>
            </thead>
            <tbody>{"".join(table_rows)}</tbody>
        </table>
        <p style="font-size:12px; color:#6b7280; margin-top:14px;">
            Red bars show inventory cost. Blue bars show backlog cost. This email contains only this player's scenario result.
        </p>
    </div>
    """


def bq_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def build_bigquery_rows(history_df, report_summary, submission_key, submitted_at_utc):
    player_round = "Round 1" if st.session_state.variant_index == 0 else "Round 2"
    base_fields = {
        "submission_id": submission_key,
        "submitted_at": submitted_at_utc,
        "player_name": st.session_state.player_name,
        "player_email": st.session_state.player_email,
        "scenario_number": int(st.session_state.variant_index + 1),
        "round_label": player_round,
        "scenario": st.session_state.scenario_title,
        "item": st.session_state.selected_item,
        "lead_time_mode": current_lead_time_mode(),
        "cost_strategy": current_cost_strategy(),
    }

    overall_rows = []
    for row in report_summary.to_dict("records"):
        overall_rows.append({
            **base_fields,
            "policy": row["Policy"],
            "months_played": int(len(history_df)),
            "final_rop": int(st.session_state.current_rop),
            "eoq": int(cfg.get_item_eoq(st.session_state.selected_item)),
            "average_stock": float(row["Average Stock"]),
            "average_pipeline": float(row["Average Pipeline"]),
            "ending_inventory": float(row["Ending Inventory"]),
            "final_stock_max": float(row["Final Stock Max"]),
            "actual_average_monthly_demand": float(row["Actual Average Monthly Demand"]),
            "actual_end_lead_time": float(row["Actual End Lead Time"]),
            "actual_demand_std_dev": float(row["Actual Demand Std Dev"]),
            "actual_safety_stock": float(row["Actual Safety Stock"]),
            "actual_rop_85": float(row["Actual ROP 85"]),
            "inventory_cost": float(row["Inventory Cost"]),
            "backlog_cost": float(row["Backlog Cost"]),
            "supplier_agreement_cost": float(row["Supplier Agreement Cost"]),
            "air_freight_cost": float(row["Air Freight Cost"]),
            "total_cost": float(row["Total Cost"]),
            "cost_points": float(row["Cost Points"]),
            "fill_rate_pct": float(row["Fill Rate"]),
            "fill_rate_penalty": float(row["Fill Rate Penalty"]),
            "excess_inventory_units": float(row["Excess Inventory Units"]),
            "overstock_penalty": float(row["Overstock Penalty"]),
            "total_penalty_points": float(row["Total Penalty"]),
        })

    detail_rows = []
    for row in history_df.to_dict("records"):
        detail_rows.append({
            **base_fields,
            "policy": "Player",
            "month_number": int(row["Month"]),
            "calendar_month": row["Calendar Month"],
            "lead_time": int(row["Lead Time"]),
            "effective_lead_time": int(row["Effective Lead Time"]),
            "rop_used": int(row["ROP Used"]),
            "eoq": int(row["EOQ"]),
            "stock_max": int(row["Stock Max"]),
            "starting_inventory": int(row["Starting Inventory"]),
            "incoming_purchases": int(row["Incoming Purchases"]),
            "inventory_after_incoming": int(row["Inventory After Incoming"]),
            "new_demand": int(row["New Demand"]),
            "backlog_from_previous_month": int(row["Backlog From Previous Month"]),
            "total_customer_need": int(row["Total Customer Need"]),
            "fulfilled": int(row["Fulfilled"]),
            "backlog_this_period": int(row["Backlog This Period"]),
            "ending_backlog": int(row["Ending Backlog"]),
            "ending_inventory": int(row["Ending Inventory"]),
            "inventory_position_before_order": int(row["Inventory Position Before Order"]),
            "reorder_triggered": row["Reorder Triggered"],
            "po_placed": int(row["PO Placed"]),
            "po_arrival_month": str(row["PO Arrival Month"]),
            "pipeline": int(row["Pipeline"]),
            "inventory_position_after_order": int(row["Inventory Position After Order"]),
            "inventory_holding_cost": float(row["Inventory Holding Cost"]),
            "backlog_cost": float(row["Backlog Cost"]),
            "supplier_agreement_cost": float(row.get("Supplier Agreement Cost", 0)),
            "air_freight_units": int(row.get("Air Freight Units", 0)),
            "air_freight_cost": float(row.get("Air Freight Cost", 0)),
            "month_total_cost": float(row["Month Total Cost"]),
            "cumulative_total_cost": float(row["Cumulative Total Cost"]),
        })

    return overall_rows, detail_rows


def make_metric_bar_chart(summary, metric_columns, metric_colors, y_title):
    chart_df = summary.melt(
        id_vars="Policy",
        value_vars=metric_columns,
        var_name="Metric",
        value_name="Value",
    )

    return (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(
                "Policy:N",
                sort=["Player", "Baseline ROP 4", "Baseline ROP 12"],
                axis=alt.Axis(labelAngle=0, title=None),
            ),
            xOffset=alt.XOffset("Metric:N"),
            y=alt.Y("Value:Q", title=y_title),
            color=alt.Color(
                "Metric:N",
                scale=alt.Scale(
                    domain=list(metric_colors.keys()),
                    range=list(metric_colors.values()),
                ),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("Policy:N"),
                alt.Tooltip("Metric:N"),
                alt.Tooltip("Value:Q", format=",.1f"),
            ],
        )
        .properties(height=320, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor="#6b7280", titleColor="#374151", gridColor="#e5e7eb")
        .configure_legend(labelColor="#6b7280", titleColor="#374151")
    )


def make_fill_rate_chart(summary):
    return (
        alt.Chart(summary)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color="#45d0c5")
        .encode(
            x=alt.X(
                "Policy:N",
                sort=["Player", "Baseline ROP 4", "Baseline ROP 12"],
                axis=alt.Axis(labelAngle=0, title=None),
            ),
            y=alt.Y("Fill Rate:Q", title="Fill rate (%)", scale=alt.Scale(domain=[0, 100])),
            tooltip=[
                alt.Tooltip("Policy:N"),
                alt.Tooltip("Fill Rate:Q", format=".1f", title="Fill Rate %"),
            ],
        )
        .properties(height=260, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor="#6b7280", titleColor="#374151", gridColor="#e5e7eb")
    )


def make_round_comparison_chart(completed_df):
    compare_df = completed_df.copy()
    if "Round" not in compare_df.columns:
        compare_df["Round"] = [f"Round {idx + 1}" for idx in range(len(compare_df))]
    chart_df = compare_df.melt(
        id_vars=["Round", "Scenario"],
        value_vars=["Total Penalty", "Average Stock", "Fill Rate"],
        var_name="Metric",
        value_name="Value",
    )
    chart_df["Metric"] = chart_df["Metric"].replace({"Total Penalty": "Penalty Points"})

    base_chart = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("Round:N", sort=["Round 1", "Round 2"], axis=alt.Axis(labelAngle=0, title=None)),
            y=alt.Y("Value:Q", title=None),
            color=alt.Color(
                "Round:N",
                scale=alt.Scale(domain=["Round 1", "Round 2"], range=["#7bc6ff", "#ffdf6b"]),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("Round:N"),
                alt.Tooltip("Scenario:N"),
                alt.Tooltip("Metric:N"),
                alt.Tooltip("Value:Q", format=",.1f"),
            ],
        )
        .properties(height=260)
    )

    return (
        base_chart
        .facet(column=alt.Column("Metric:N", title=None))
        .properties(background="transparent")
        .resolve_scale(y="independent")
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor="#6b7280", titleColor="#374151", gridColor="#e5e7eb")
        .configure_legend(labelColor="#6b7280", titleColor="#374151")
    )


def make_trend_chart(report_trends, metric):
    return (
        alt.Chart(report_trends)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("Month:O", title="Month"),
            y=alt.Y(f"{metric}:Q", title=metric),
            color=alt.Color(
                "Policy:N",
                scale=alt.Scale(
                    domain=["Player", "Baseline ROP 4", "Baseline ROP 12"],
                    range=["#ffdf6b", "#7bc6ff", "#ff6b6b"],
                ),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("Month:O"),
                alt.Tooltip("Policy:N"),
                alt.Tooltip(f"{metric}:Q", format=",.1f"),
            ],
        )
        .properties(height=340, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor="#6b7280", titleColor="#374151", gridColor="#e5e7eb")
        .configure_legend(labelColor="#6b7280", titleColor="#374151")
    )


# =========================================================
# SECTION 6: ANIMATION
# =========================================================

def animate_month(row):
    incoming_move_html = '<div class="moving1">📦 📦 📦</div>' if row["Incoming Purchases"] > 0 else ""
    fulfilled_move_html = '<div class="moving2">🔩 🔩 🔩</div>' if row["Fulfilled"] > 0 else ""
    demand_pop_html = '<div class="demand-pop">🧍 🧍 🧍</div>' if row["New Demand"] > 0 else ""
    po_move_html = '<div class="moving-po">📄<span>PO</span></div>' if row["Reorder Triggered"] == "Yes" else ""
    sound_calls = []
    if row["Incoming Purchases"] > 0:
        sound_calls.append("playTone(420, 0.05, 0.22, 0.045);")
    if row["Fulfilled"] > 0:
        sound_calls.append("playTone(620, 0.06, 0.18, 0.035);")
    if row["Reorder Triggered"] == "Yes":
        sound_calls.append("playTone(880, 0.72, 0.10, 0.035); playTone(1170, 0.84, 0.12, 0.03);")

    supplier_node = render_node_html(
        "📦 Supplier",
        "Pipeline / open orders",
        row["Pipeline"],
        "📦",
        "#7e57ff"
    )

    inventory_node = render_inventory_timing_block_html(
        row["Inventory After Incoming"],
        row["Ending Inventory"],
        row["Inventory Position After Order"],
        "#1fd0c1"
    )

    customer_node = render_node_html(
        "👥 Customers",
        "Current demand",
        row["New Demand"],
        "🧍",
        "#ffb347"
    )

    po_message = "Order-up-to replenishment created" if row["Reorder Triggered"] == "Yes" else "No order created"
    po_detail = (
        f"PO Qty: {row['PO Placed']} | Stock Max: {row['Stock Max']} | Arrival: {row['PO Arrival Month']}"
        if row["Reorder Triggered"] == "Yes"
        else "Inventory position stayed above ROP"
    )

    lead_time_alert = get_lead_time_alert(row["Month"])
    alert_html = ""
    if lead_time_alert:
        alert_class = "lt-alert-up" if lead_time_alert["kind"] == "increase" else "lt-alert-down"
        alert_emoji = "🚨" if lead_time_alert["kind"] == "increase" else "📣"

        alert_html = f"""
        <div class="lt-alert {alert_class}">
            <div class="lt-alert-emoji">{alert_emoji}</div>
            <div>
                <div class="lt-alert-title">{lead_time_alert["title"]}</div>
                <div class="lt-alert-message">{lead_time_alert["message"]}</div>
            </div>
            <div class="lt-alert-emoji">{alert_emoji}</div>
        </div>
        """

    animation_html = f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: transparent;
            color: white;
        }}

        .wrap {{
            border: 1px solid rgba(129, 149, 255, 0.18);
            border-radius: 20px;
            padding: 16px;
            background:
                radial-gradient(circle at top left, rgba(86,72,194,0.20), transparent 22%),
                linear-gradient(180deg, rgba(5,9,18,0.98), rgba(6,9,17,0.98));
            box-shadow: 0 16px 38px rgba(0,0,0,0.34);
            min-height: 980px;
        }}

        .title {{
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 4px;
            color: #ffffff;
        }}

        .subtitle {{
            color: #ffffff;
            margin-bottom: 14px;
            font-size: 1rem;
        }}

        .lt-alert {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 14px;
            margin-bottom: 14px;
            border-radius: 18px;
            padding: 12px 16px;
            font-weight: 800;
            box-shadow: 0 10px 25px rgba(0,0,0,0.30);
            animation: popIn 0.5s ease, floaty 1.5s ease-in-out infinite;
        }}

        .lt-alert-up {{
            background: linear-gradient(90deg, rgba(255,96,96,0.96), rgba(255,166,77,0.96));
            border: 2px solid rgba(255,255,255,0.24);
            color: white;
        }}

        .lt-alert-down {{
            background: linear-gradient(90deg, rgba(50,190,140,0.96), rgba(55,145,255,0.96));
            border: 2px solid rgba(255,255,255,0.24);
            color: white;
        }}

        .lt-alert-emoji {{
            font-size: 2rem;
            animation: wiggle 0.8s ease-in-out infinite;
        }}

        .lt-alert-title {{
            font-size: 1.2rem;
            text-align: center;
        }}

        .lt-alert-message {{
            font-size: 0.95rem;
            text-align: center;
            margin-top: 2px;
        }}

        .flow {{
            display: grid;
            grid-template-columns: 1fr 70px 1fr 70px 1fr;
            align-items: start;
            gap: 10px;
            position: relative;
            min-height: 440px;
        }}

        .col {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .arrow {{
            text-align: center;
            font-size: 2rem;
            color: #ffffff;
            padding-top: 95px;
        }}

        .arrow-label {{
            font-size: 0.82rem;
            color: #ffffff;
            margin-top: 3px;
            font-weight: 700;
        }}

        .moving1 {{
            position: absolute;
            top: 82px;
            left: 11%;
            font-size: 1.9rem;
            opacity: 0;
            animation: supplier_to_inventory 1.2s ease-in-out forwards;
        }}

        .moving2 {{
            position: absolute;
            top: 165px;
            left: 45%;
            font-size: 1.9rem;
            opacity: 0;
            animation: inventory_to_customers 1.2s ease-in-out forwards;
            animation-delay: 0s;
        }}

        .moving-po {{
            position: absolute;
            top: 116px;
            left: 43%;
            font-size: 2rem;
            opacity: 0;
            animation: warehouse_to_supplier_po 1.05s ease-in-out forwards;
            animation-delay: 0.25s;
            z-index: 5;
            filter: drop-shadow(0 8px 14px rgba(0,0,0,0.35));
        }}

        .moving-po span {{
            position: absolute;
            left: 7px;
            top: 13px;
            font-size: 0.48rem;
            font-weight: 900;
            color: #111827;
        }}

        .demand-pop {{
            position: absolute;
            top: 20px;
            right: 6%;
            font-size: 1.9rem;
            opacity: 0;
            animation: demand_appear 0.8s ease forwards;
            animation-delay: 0.65s;
        }}

        @keyframes supplier_to_inventory {{
            0% {{ left: 11%; opacity: 0; }}
            10% {{ opacity: 1; }}
            100% {{ left: 41%; opacity: 1; }}
        }}

        @keyframes inventory_to_customers {{
            0% {{ left: 45%; opacity: 0; }}
            10% {{ opacity: 1; }}
            100% {{ left: 78%; opacity: 1; }}
        }}

        @keyframes warehouse_to_supplier_po {{
            0% {{ left: 43%; opacity: 0; transform: rotate(-6deg) scale(0.8); }}
            10% {{ opacity: 1; }}
            100% {{ left: 12%; opacity: 1; transform: rotate(7deg) scale(1.05); }}
        }}

        @keyframes demand_appear {{
            0% {{ opacity: 0; transform: scale(0.55); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}

        @keyframes wiggle {{
            0% {{ transform: rotate(0deg); }}
            25% {{ transform: rotate(-8deg); }}
            50% {{ transform: rotate(8deg); }}
            75% {{ transform: rotate(-6deg); }}
            100% {{ transform: rotate(0deg); }}
        }}

        @keyframes floaty {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-3px); }}
            100% {{ transform: translateY(0px); }}
        }}

        @keyframes popIn {{
            0% {{ opacity: 0; transform: scale(0.92); }}
            100% {{ opacity: 1; transform: scale(1); }}
        }}

        .mini-grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }}

        .mini-grid-3,
        .mini-grid-4 {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
        }}

        .mini {{
            border: 1px solid rgba(129, 149, 255, 0.14);
            border-radius: 12px;
            background: rgba(12, 19, 43, 0.88);
            padding: 8px;
            text-align: center;
            min-height: 62px;
        }}

        .mini-label {{
            font-size: 0.73rem;
            color: #ffffff;
            line-height: 1.15;
        }}

        .mini-value {{
            font-size: 1.2rem;
            font-weight: 900;
            margin-top: 5px;
            color: white;
        }}

        .cost-mini {{
            border: 1px solid rgba(255, 80, 80, 0.28);
            background: rgba(60, 10, 18, 0.92);
        }}

        .cost-value {{
            color: #ff6b6b !important;
        }}

        .po-box {{
            margin-top: 14px;
            border-radius: 16px;
            padding: 12px 14px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
        }}

        .po-title {{
            font-size: 1.1rem;
            font-weight: 800;
        }}

        .po-detail {{
            margin-top: 4px;
            font-size: 0.95rem;
        }}
    </style>
    </head>
    <body>
        <div class="wrap">
            <div class="title">{row["Calendar Month"]} flow</div>
            <div class="subtitle">{row["Item"]} | Effective lead time this month: {row["Effective Lead Time"]} month(s) | ROP used: {row["ROP Used"]} | EOQ: {row["EOQ"]}</div>

            {alert_html}

            <div class="flow">
                {incoming_move_html}
                {fulfilled_move_html}
                {demand_pop_html}
                {po_move_html}

                <div class="col">
                    {supplier_node}
                    <div class="mini-grid-2">
                        <div class="mini">
                            <div class="mini-label">Pipeline</div>
                            <div class="mini-value">{row["Pipeline"]}</div>
                        </div>
                        <div class="mini">
                            <div class="mini-label">Effective Lead Time</div>
                            <div class="mini-value">{row["Effective Lead Time"]}</div>
                        </div>
                    </div>
                </div>

                <div class="arrow">➡️<div class="arrow-label">Incoming</div></div>

                <div class="col">
                    {inventory_node}
                    <div class="mini-grid-3">
                        <div class="mini">
                            <div class="mini-label">Ending Stock After Demand</div>
                            <div class="mini-value">{row["Ending Inventory"]}</div>
                        </div>
                        <div class="mini">
                            <div class="mini-label">Warehouse Position Before Order</div>
                            <div class="mini-value">{row["Inventory Position Before Order"]}</div>
                        </div>
                        <div class="mini cost-mini">
                            <div class="mini-label">Warehouse Cost</div>
                            <div class="mini-value cost-value">{int(row["Inventory Holding Cost"])}</div>
                        </div>
                        <div class="mini cost-mini">
                            <div class="mini-label">Strategy Cost</div>
                            <div class="mini-value cost-value">{int(row.get("Supplier Agreement Cost", 0) + row.get("Air Freight Cost", 0))}</div>
                        </div>
                    </div>
                </div>

                <div class="arrow">➡️<div class="arrow-label">Serve</div></div>

                <div class="col">
                    {customer_node}
                    <div class="mini-grid-4">
                        <div class="mini">
                            <div class="mini-label">Fulfilled</div>
                            <div class="mini-value">{row["Fulfilled"]}</div>
                        </div>
                        <div class="mini">
                            <div class="mini-label">Backlog This Period</div>
                            <div class="mini-value">{row["Backlog This Period"]}</div>
                        </div>
                        <div class="mini">
                            <div class="mini-label">Total Backlog</div>
                            <div class="mini-value">{row["Ending Backlog"]}</div>
                        </div>
                        <div class="mini cost-mini">
                            <div class="mini-label">Total Backlog Cost</div>
                            <div class="mini-value cost-value">{int(row["Backlog Cost"])}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="po-box">
                <div class="po-title">{po_message}</div>
                <div class="po-detail">{po_detail}</div>
            </div>
        </div>
        <script>
            function playTone(freq, start, duration, gain) {{
                try {{
                    const AudioCtx = window.AudioContext || window.webkitAudioContext;
                    const ctx = new AudioCtx();
                    const osc = ctx.createOscillator();
                    const volume = ctx.createGain();
                    osc.type = "triangle";
                    osc.frequency.setValueAtTime(freq, ctx.currentTime + start);
                    volume.gain.setValueAtTime(0.0001, ctx.currentTime + start);
                    volume.gain.exponentialRampToValueAtTime(gain, ctx.currentTime + start + 0.03);
                    volume.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + start + duration);
                    osc.connect(volume);
                    volume.connect(ctx.destination);
                    osc.start(ctx.currentTime + start);
                    osc.stop(ctx.currentTime + start + duration + 0.04);
                }} catch (e) {{
                    // Some browsers block autoplayed sound. The animation still runs.
                }}
            }}
            {" ".join(sound_calls)}
        </script>
    </body>
    </html>
    """

    html(animation_html, height=900)


# =========================================================
# SECTION 7: HEADER
# =========================================================

st.markdown("""
<div class="top-title-card">
    <div class="top-title">📊 Spare Parts ROP / EOQ Planning Game</div>
    <div class="top-subtitle">Adjust the reorder point, let the system order automatically, and manage the impact of lead-time shocks.</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# SECTION 8: PLAYER REGISTRATION
# =========================================================

if not st.session_state.player_ready:
    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    st.markdown("""
    <div class="intro-shell">
        <div class="intro-kicker">Welcome to the inventory planning challenge</div>
        <div class="intro-heading">Slow-moving spare part planning game</div>
        <div class="intro-copy">
            First you will play the original slow-moving spare part round with constant lead time.
            After the first report, you will choose one second-round strategy: supplier agreement
            or air freight. Control the ROP month by month and watch stock, pipeline, backlog, service, and cost.
        </div>
        <div class="intro-grid">
            <div class="intro-step">
                <div class="intro-step-number">1</div>
                <div class="intro-step-title">First round</div>
                <div class="intro-step-text">The old slow-mover constant lead-time game.</div>
            </div>
            <div class="intro-step">
                <div class="intro-step-number">2</div>
                <div class="intro-step-title">Second-round choice</div>
                <div class="intro-step-text">Choose supplier agreement or air freight.</div>
            </div>
            <div class="intro-step">
                <div class="intro-step-number">3</div>
                <div class="intro-step-title">Your decision</div>
                <div class="intro-step-text">Set the ROP each month while demand, stock, pipeline, and backlog evolve.</div>
            </div>
            <div class="intro-step">
                <div class="intro-step-number">4</div>
                <div class="intro-step-title">Performance report</div>
                <div class="intro-step-text">Compare your result with baseline ROP 4 and ROP 12 solutions.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="section-title">Player information</div>', unsafe_allow_html=True)

    name_input = st.text_input("Your name")
    email_input = st.text_input("Your email")

    start_clicked = st.button("Start game", type="primary")

    if start_clicked:
        if not name_input.strip():
            st.error("Please enter your name.")
        elif not valid_email(email_input):
            st.error("Please enter a valid email address.")
        else:
            st.session_state.player_name = name_input.strip()
            st.session_state.player_email = email_input.strip().lower()
            st.session_state.variant_index = 0
            st.session_state.player_ready = True
            init_game()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


if not st.session_state.get("scenario_notice_seen", False):
    if hasattr(st, "dialog"):
        @st.dialog(st.session_state.scenario_title)
        def show_scenario_notice():
            scenario_number = 1 if st.session_state.variant_index == 0 else 2
            total_scenarios = 2
            st.markdown(f"## Scenario {scenario_number} / {total_scenarios}")
            st.markdown(st.session_state.scenario_intro)
            st.markdown(f"**Cost rule:** {strategy_cost_explanation()}")
            st.markdown("Review the planning logic, demand timeline, current inventory position, and lead-time information before playing the first month.")
            if st.button("Start this scenario", type="primary"):
                st.session_state.scenario_notice_seen = True
                st.rerun()

        show_scenario_notice()
    else:
        st.info(st.session_state.scenario_intro)
        st.session_state.scenario_notice_seen = True


# =========================================================
# SECTION 9: PLANNING LOGIC + COMBINED DEMAND GRAPH
# =========================================================

current_item = st.session_state.selected_item
current_initial_inventory = cfg.get_item_initial_inventory(current_item)
current_initial_rop = cfg.get_item_initial_rop(current_item)
current_eoq = cfg.get_item_eoq(current_item)
if current_lead_time_mode() == "constant":
    lead_time_rule_text = "Lead time: constant at 1 month throughout the game."
elif current_cost_strategy() == "supplier_agreement":
    lead_time_rule_text = "Market lead time can change, but the supplier agreement keeps effective replenishment lead time at 1 month."
elif current_cost_strategy() == "air_freight":
    lead_time_rule_text = "Market lead time can change. Air freight only applies during the 3-month lead-time shock and changes replenishment PO lead time to 1 month, not instant delivery."
else:
    lead_time_rule_text = "Lead time: Month 1-2 = 1 month, Month 3-7 = 3 months, Month 8-12 = 1 month."

strategy_cost_text = {
    "supplier_agreement": strategy_cost_explanation("supplier_agreement"),
    "air_freight": strategy_cost_explanation("air_freight"),
}.get(current_cost_strategy(), strategy_cost_explanation("none"))

st.markdown(f"""
<div class="dashboard-panel" style="padding:14px 18px; border:1px solid rgba(255,223,107,0.35);">
    <div style="font-size:1.65rem; font-weight:900; color:white;">🎯 Currently Playing</div>
    <div style="font-size:1.25rem; font-weight:800; color:#ffdf6b; margin-top:4px;">{current_item}</div>
    <div style="font-size:1rem; font-weight:800; color:#bffaf4; margin-top:4px;">{st.session_state.scenario_title}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="scenario-ribbon">{st.session_state.scenario_title}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="cost-box">
    <div style="font-size:1.05rem; font-weight:800; margin-bottom:8px; color:white;">Planning Logic for Current Item</div>
    <div class="small-note">• Initial Inventory = {current_initial_inventory}</div>
    <div class="small-note">• Initial ROP = {current_initial_rop}</div>
    <div class="small-note">• EOQ = {current_eoq}</div>
    <div class="small-note">• Stock Max = ROP + EOQ.</div>
    <div class="small-note">• Reorder rule: if Inventory Position ≤ ROP, order quantity = Stock Max - Inventory Position.</div>
    <div class="small-note">• Inventory Position = Stock on Hand + Pipeline - Backorders.</div>
    <div class="small-note">• {lead_time_rule_text}</div>
    <div style="margin-top:10px;">
        <span class="cost-chip">Inventory Holding Cost = Ending Inventory × {cfg.holding_cost_per_unit}</span>
        <span class="cost-chip">Backlog Cost = Ending Backlog × {cfg.backlog_cost_per_unit}</span>
        <span class="cost-chip">{strategy_cost_text}</span>
        <span class="cost-chip">Scoring: each cost unit becomes 1 penalty point</span>
        <span class="cost-chip">Fill-rate penalty: below {TARGET_FILL_RATE_PERCENT:.0f}% costs {FILL_RATE_PENALTY_PER_PERCENT:.0f} points per percentage point</span>
        <span class="cost-chip">End benchmark: Actual ROP = End Lead Time x Avg Demand + Safety Stock</span>
        <span class="cost-chip">End Lead Time for the benchmark = lead time at game end (normally 1 month)</span>
        <span class="cost-chip">Safety Stock for 85% = 1 × actual demand stdev</span>
        <span class="cost-chip">End Stock Max = Actual ROP + EOQ; ending stock above this costs {OVERSTOCK_PENALTY_PER_UNIT:.0f} points per unit</span>
    </div>
</div>
""", unsafe_allow_html=True)

month_now = st.session_state.month
month_shown = min(month_now, cfg.months)

rop_advice = get_rop_advice(st.session_state.selected_item)
current_inventory_position = inventory_position()
recommended_rop = rop_advice["recommended_rop"]
gap_to_recommended = recommended_rop - st.session_state.current_rop
inventory_position_gap = current_inventory_position - recommended_rop

if gap_to_recommended > 0:
    rop_status = f"Your current ROP is {gap_to_recommended} below the history-based suggestion."
elif gap_to_recommended < 0:
    rop_status = f"Your current ROP is {abs(gap_to_recommended)} above the history-based suggestion."
else:
    rop_status = "Your current ROP matches the history-based suggestion."

if inventory_position_gap < 0:
    position_status = f"Inventory position is {abs(inventory_position_gap)} below the suggested ROP, so a reorder is likely if you keep this setting."
else:
    position_status = f"Inventory position is {inventory_position_gap} above the suggested ROP."

st.markdown(f"""
<div class="cost-box" style="border-color:rgba(69,208,197,0.35);">
    <div style="font-size:1.05rem; font-weight:800; margin-bottom:8px; color:white;">Decision Coach</div>
    <div class="small-note">Inventory Position = Stock on Hand + On Order - Backlog.</div>
    <div class="small-note">For the ROP guide, average lead time is 1 month and the fill-rate target is 85% (z value = 1).</div>
    <div style="margin-top:10px;">
        <span class="cost-chip">Average Monthly Demand = {rop_advice["average_monthly_demand"]:.1f}</span>
        <span class="cost-chip">Average Lead Time = {rop_advice["average_lead_time"]} month</span>
        <span class="cost-chip">Safety Stock = {rop_advice["z_value"]} × {rop_advice["demand_std_dev"]:.1f} = {rop_advice["safety_stock"]:.1f}</span>
        <span class="cost-chip">ROP = {rop_advice["average_lead_time"]} × {rop_advice["average_monthly_demand"]:.1f} + {rop_advice["safety_stock"]:.1f} = {recommended_rop}</span>
        <span class="cost-chip">Suggested ROP = {recommended_rop}</span>
    </div>
    <div class="small-note" style="margin-top:10px;">{rop_status}</div>
    <div class="small-note">{position_status}</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# SECTION 10: TOP STATUS + CONTROLS
# =========================================================

st.caption(f"Player: {st.session_state.player_name} | {st.session_state.player_email} | Scenario: {st.session_state.scenario_title}")

st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)

status1, status2, status3, status4 = st.columns(4)

status1.metric("Current Month", f"{month_shown} / {cfg.months}", get_game_month_label(month_shown))
status2.metric("Current ROP", st.session_state.current_rop)
status3.metric("Current EOQ", cfg.get_item_eoq(st.session_state.selected_item))
status4.metric("Stock Max", st.session_state.current_rop + cfg.get_item_eoq(st.session_state.selected_item))

inv1, inv2, inv3, inv4, inv5 = st.columns(5)
inv1.metric("Inventory On Hand", st.session_state.inventory)
inv2.metric("Pipeline", pipeline_total())
inv3.metric("Inventory Position", inventory_position())
inv4.metric("Backlog", st.session_state.backlog)
base_lead_time_now = cfg.lead_time(month_shown, current_lead_time_mode())
effective_lead_time_now = effective_lead_time_for_strategy(base_lead_time_now, current_cost_strategy())
inv5.metric("Effective Lead Time", effective_lead_time_now)

st.markdown('</div>', unsafe_allow_html=True)

if month_now <= cfg.months:
    st.caption(f"Demand for {get_game_month_label(month_shown)}: hidden until you play this month")

lead_time_event = get_lead_time_alert(month_now, current_lead_time_mode())
lead_time_event_key = f"{current_lead_time_mode()}-{month_now}"
if (
    lead_time_event
    and lead_time_event_key not in st.session_state.lead_time_event_seen
    and month_now <= cfg.months
):
    if hasattr(st, "dialog"):
        @st.dialog(lead_time_event["title"])
        def show_lead_time_event():
            event_emoji = "🚨" if lead_time_event["kind"] == "increase" else "🎉"
            st.markdown(f"## {event_emoji} {lead_time_event['message']}")
            st.markdown("Read the new lead-time situation carefully before choosing this month's ROP.")
            if st.button("Got it - choose my ROP", type="primary", use_container_width=True):
                st.session_state.lead_time_event_seen.append(lead_time_event_key)
                st.rerun()

        show_lead_time_event()
    else:
        st.session_state.lead_time_event_seen.append(lead_time_event_key)
        st.warning(lead_time_event["message"])

if current_lead_time_mode() == "changing" and month_now == cfg.shock_month:
    st.warning(f"Lead time shock starts now: lead time increased from {cfg.initial_lead_time} to {cfg.shocked_lead_time} months.")
elif current_lead_time_mode() == "changing" and month_now == cfg.full_recovery_month:
    st.success(f"Full recovery starts now: lead time returns to {cfg.recovered_lead_time} month.")

combined_chart_small = build_combined_demand_svg(st.session_state.selected_item, compact=True)
st.markdown(combined_chart_small, unsafe_allow_html=True)

st.markdown('<div class="decision-panel"><div class="decision-panel-title">Next monthly decision</div>', unsafe_allow_html=True)
decision_col1, decision_col2, decision_col3, decision_col4 = st.columns([1.15, 3.5, 1.25, 1.05])
with decision_col1:
    st.markdown(
        f'<div class="decision-month-pill"><span>Game Month</span><strong>{month_shown} / {cfg.months}</strong></div>',
        unsafe_allow_html=True,
    )
with decision_col2:
    st.markdown('<div class="decision-row-label">ROP for this month</div>', unsafe_allow_html=True)
    rop = st.slider(
        "ROP for this month",
        min_value=0,
        max_value=150,
        value=int(st.session_state.current_rop),
        step=1,
        label_visibility="collapsed",
        help="The system compares Inventory Position with this ROP after demand is served. Inventory Position = Stock on Hand + Pipeline - Backorders."
    )
with decision_col3:
    st.markdown('<div class="decision-row-label">&nbsp;</div>', unsafe_allow_html=True)
    play = st.button("▶ Play next month", type="primary", use_container_width=True)
with decision_col4:
    st.markdown('<div class="decision-row-label">&nbsp;</div>', unsafe_allow_html=True)
    reset = st.button("↻ Reset", type="secondary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if reset:
    selected_item_before_reset = st.session_state.selected_item
    player_name_before_reset = st.session_state.player_name
    player_email_before_reset = st.session_state.player_email
    init_game()
    st.session_state.selected_item = selected_item_before_reset
    st.session_state.player_name = player_name_before_reset
    st.session_state.player_email = player_email_before_reset
    st.session_state.player_ready = True
    st.rerun()

if play:
    if st.session_state.month <= cfg.months:
        row = run_month(rop)
        animate_month(row)
    else:
        st.info("Game finished. Result will be submitted automatically.")



# =========================================================
# SECTION 11: KPI SUMMARY
# =========================================================

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)

    total_need = df["Total Customer Need"].sum()
    total_fulfilled = df["Fulfilled"].sum()
    service_level = total_fulfilled / total_need if total_need > 0 else 0

    total_inventory_cost = df["Inventory Holding Cost"].sum()
    total_backlog_cost = df["Backlog Cost"].sum()
    total_strategy_cost = df.get("Supplier Agreement Cost", pd.Series([0])).sum() + df.get("Air Freight Cost", pd.Series([0])).sum()
    cumulative_total_cost = df["Cumulative Total Cost"].iloc[-1]

    kpi_html = textwrap.dedent(f"""
    <div style="padding:16px; font-family: Arial, sans-serif;">
        <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap:12px;">
            <div style="background:rgba(9,18,48,0.85); border:1px solid rgba(120,140,255,0.18); border-radius:16px; padding:12px;">
                <div style="color:white; font-size:0.95rem;">Service Level</div>
                <div style="color:white; font-size:1.8rem; font-weight:800;">{service_level:.1%}</div>
            </div>
            <div style="background:rgba(60,10,18,0.92); border:1px solid rgba(255,80,80,0.28); border-radius:16px; padding:12px;">
                <div style="color:white; font-size:0.95rem;">Total Inventory Cost</div>
                <div style="color:#ff6b6b; font-size:1.8rem; font-weight:800;">{total_inventory_cost:,.0f}</div>
            </div>
            <div style="background:rgba(60,10,18,0.92); border:1px solid rgba(255,80,80,0.28); border-radius:16px; padding:12px;">
                <div style="color:white; font-size:0.95rem;">Total Backlog Cost</div>
                <div style="color:#ff6b6b; font-size:1.8rem; font-weight:800;">{total_backlog_cost:,.0f}</div>
            </div>
            <div style="background:rgba(60,10,18,0.92); border:1px solid rgba(255,223,107,0.30); border-radius:16px; padding:12px;">
                <div style="color:white; font-size:0.95rem;">Strategy Cost</div>
                <div style="color:#ffdf6b; font-size:1.8rem; font-weight:800;">{total_strategy_cost:,.0f}</div>
            </div>
            <div style="background:rgba(60,10,18,0.92); border:1px solid rgba(255,80,80,0.28); border-radius:16px; padding:12px;">
                <div style="color:white; font-size:0.95rem;">Cumulative Total Cost</div>
                <div style="color:#ff6b6b; font-size:1.8rem; font-weight:800;">{cumulative_total_cost:,.0f}</div>
            </div>
        </div>
    </div>
    """)

    html(kpi_html, height=150)


# =========================================================
# SECTION 12: AUTO-SUBMIT WHEN GAME ENDS
# =========================================================

submission_key = f"{st.session_state.player_email}|{st.session_state.variant_index}|{st.session_state.get('scenario_title', '')}"

if (
    st.session_state.history
    and st.session_state.month > cfg.months
    and submission_key not in st.session_state.submitted_scenario_keys
):
    df = pd.DataFrame(st.session_state.history)

    total_need = df["Total Customer Need"].sum()
    total_fulfilled = df["Fulfilled"].sum()
    service_level = total_fulfilled / total_need if total_need > 0 else 0

    total_inventory_cost = df["Inventory Holding Cost"].sum()
    total_backlog_cost = df["Backlog Cost"].sum()
    total_supplier_agreement_cost = df.get("Supplier Agreement Cost", pd.Series([0])).sum()
    total_air_freight_cost = df.get("Air Freight Cost", pd.Series([0])).sum()
    cumulative_total_cost = df["Cumulative Total Cost"].iloc[-1]
    report_summary, _ = build_performance_report(
        st.session_state.history,
        st.session_state.selected_item,
        current_lead_time_mode(),
        current_cost_strategy(),
    )
    submitted_at_utc = datetime.now(timezone.utc).isoformat()
    overall_rows, detail_rows = build_bigquery_rows(
        df,
        report_summary,
        submission_key,
        submitted_at_utc,
    )

    payload = {
        "destination": "bigquery",
        "overall_table": "inventory_game_round_results",
        "detail_table": "inventory_game_monthly_details",
        "submitted_at": submitted_at_utc,
        "player_name": st.session_state.player_name,
        "player_email": st.session_state.player_email,
        "player_report_email": st.session_state.player_email,
        "admin_report_email": ADMIN_REPORT_EMAIL,
        "email_recipients": [st.session_state.player_email, ADMIN_REPORT_EMAIL],
        "item": st.session_state.selected_item,
        "scenario": st.session_state.scenario_title,
        "scenario_number": st.session_state.variant_index + 1,
        "scenario_key": submission_key,
        "lead_time_mode": current_lead_time_mode(),
        "cost_strategy": current_cost_strategy(),
        "service_level": round(service_level * 100, 1),
        "total_inventory_cost": round(total_inventory_cost, 0),
        "total_backlog_cost": round(total_backlog_cost, 0),
        "total_supplier_agreement_cost": round(total_supplier_agreement_cost, 0),
        "total_air_freight_cost": round(total_air_freight_cost, 0),
        "cumulative_total_cost": round(cumulative_total_cost, 0),
        "months_played": len(st.session_state.history),
        "final_rop": int(st.session_state.current_rop),
        "eoq": cfg.get_item_eoq(st.session_state.selected_item),
        "overall_rows": overall_rows,
        "detail_rows": detail_rows,
        "report_summary": report_summary.to_dict("records"),
        "report_html": build_email_report_html(
            report_summary,
            st.session_state.player_name,
            st.session_state.player_email,
            st.session_state.scenario_title,
            st.session_state.selected_item,
            current_lead_time_mode(),
        ),
    }

    if not results_submission_configured():
        st.session_state.submitted = True
        st.session_state.submitted_scenario_keys.append(submission_key)
        st.info("BigQuery submission is not configured yet, so this run was kept local.")
    else:
        try:
            response = submit_result_to_bigquery_endpoint(payload)
            response_json = {}
            response_ok = False
            try:
                response_json = response.json()
                response_ok = response.status_code == 200 and response_json.get("ok") is True
            except ValueError:
                response_ok = False

            if response_ok:
                st.session_state.submitted = True
                st.session_state.submitted_scenario_keys.append(submission_key)
                st.success("Your result has been submitted to BigQuery.")
            else:
                st.session_state.submitted = True
                st.session_state.submitted_scenario_keys.append(submission_key)
                endpoint_error = response_json.get("error") if response_json else response.text[:500]
                st.session_state.submission_warning = (
                    "The report was generated, but BigQuery submission did not confirm success. "
                    f"Please check the Apps Script BigQuery deployment and permissions. Endpoint response: {endpoint_error}"
                )

        except Exception as e:
            st.session_state.submitted = True
            st.session_state.submitted_scenario_keys.append(submission_key)
            st.session_state.submission_warning = (
                "The report was generated, but this computer could not connect to the BigQuery submission endpoint. "
                "This usually happens when Python cannot reach script.google.com through the local network or proxy."
            )

if st.session_state.get("submission_warning"):
    st.warning(st.session_state.submission_warning)


# =========================================================
# SECTION 12B: PERFORMANCE REPORT + NEXT SCENARIO
# =========================================================

if st.session_state.history and st.session_state.month > cfg.months:
    if st.session_state.variant_index == 0:
        st.markdown('<div class="round2-ribbon-marker"></div>', unsafe_allow_html=True)
        if st.button("Open Round 2 ↓", key="round2_ribbon_button"):
            st.session_state.second_round_popup_step = "briefing" if hasattr(st, "dialog") else "inline"
            st.rerun()

    report_summary, report_trends = build_performance_report(
        st.session_state.history,
        st.session_state.selected_item,
        current_lead_time_mode(),
        current_cost_strategy(),
    )

    if not st.session_state.get("round_complete_seen", False):
        if hasattr(st, "dialog"):
            @st.dialog("Round complete!")
            def show_round_complete():
                st.markdown("## 🎉 Round is complete")
                for feedback_line in build_round_complete_feedback(
                    report_summary,
                    st.session_state.variant_index,
                    st.session_state.completed_reports,
                ):
                    st.markdown(f"- {feedback_line}")
                if st.session_state.variant_index == 0:
                    st.markdown("Review the result report, then click the tall colorful **Open Round 2** ribbon on the right.")
                else:
                    st.markdown("Review the result report below. The top KPI block compares this round with your first round.")
                if st.button("Show my results", type="primary", use_container_width=True):
                    st.session_state.round_complete_seen = True
                    st.balloons()
                    st.rerun()

            show_round_complete()
        else:
            st.session_state.round_complete_seen = True
            st.balloons()

    if not st.session_state.get("report_saved_current", False):
        player_summary = report_summary[report_summary["Policy"] == "Player"].iloc[0].to_dict()
        player_summary["Round"] = "Round 1" if st.session_state.variant_index == 0 else "Round 2"
        player_summary["Scenario"] = st.session_state.scenario_title
        player_summary["Item"] = st.session_state.selected_item
        player_summary["Lead Time Mode"] = current_lead_time_mode()
        player_summary["Cost Strategy"] = current_cost_strategy()
        st.session_state.completed_reports.append(player_summary)
        st.session_state.report_saved_current = True

    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    st.markdown("""
    <div class="round-complete-card">
        <div class="round-complete-title">Round complete - results are ready</div>
        <div class="round-complete-text">Review your scorecards and charts below, then continue to the next game.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="report-hero">
        <div class="report-eyebrow">Scenario report</div>
        <div class="report-title">{st.session_state.scenario_title}</div>
        <div class="report-subtitle">Player performance compared with fixed ROP baselines 4 and 12.</div>
        <div class="report-subtitle">Penalty points = total cost + fill-rate penalty + overstock penalty.</div>
        <div class="report-subtitle">Fill rate below {TARGET_FILL_RATE_PERCENT:.0f}% = {FILL_RATE_PENALTY_PER_PERCENT:.0f} points per percentage point. Ending stock above the actual-demand Stock Max = {OVERSTOCK_PENALTY_PER_UNIT:.0f} points per unit.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        render_penalty_overview(report_summary, st.session_state.variant_index, st.session_state.completed_reports),
        unsafe_allow_html=True,
    )
    if st.session_state.variant_index != 0 and len(st.session_state.completed_reports) >= 2:
        completed_df_top = pd.DataFrame(st.session_state.completed_reports)
        if "Round" not in completed_df_top.columns:
            completed_df_top["Round"] = [f"Round {idx + 1}" for idx in range(len(completed_df_top))]
        comparison_cols = ["Round", "Scenario", "Cost Strategy", "Average Stock", "Total Penalty", "Fill Rate"]
        comparison_table = completed_df_top[[col for col in comparison_cols if col in completed_df_top.columns]].rename(
            columns={"Total Penalty": "Penalty Points"}
        )
        st.markdown('<div class="chart-panel"><div class="chart-title">Main KPI comparison: Round 1 vs Round 2</div>', unsafe_allow_html=True)
        st.altair_chart(make_round_comparison_chart(completed_df_top), use_container_width=True)
        st.dataframe(comparison_table, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(render_scorecards(report_summary), unsafe_allow_html=True)
    player_report = report_summary[report_summary["Policy"] == "Player"].iloc[0]
    st.markdown(f"""
    <div class="cost-box" style="border-color:rgba(69,208,197,0.35);">
        <div style="font-size:1.05rem; font-weight:800; margin-bottom:8px; color:white;">End-of-game Stock Max benchmark</div>
        <div class="small-note">Calculated from actual game demand and the lead time at the end of this round.</div>
        <div style="margin-top:10px;">
            <span class="cost-chip">Average Monthly Demand = {player_report["Actual Average Monthly Demand"]:.1f}</span>
            <span class="cost-chip">End Lead Time = {player_report["Actual End Lead Time"]:.1f} month(s)</span>
            <span class="cost-chip">Safety Stock = 1 × {player_report["Actual Demand Std Dev"]:.1f} = {player_report["Actual Safety Stock"]:.1f}</span>
            <span class="cost-chip">Actual ROP 85 = {player_report["Actual End Lead Time"]:.1f} × {player_report["Actual Average Monthly Demand"]:.1f} + {player_report["Actual Safety Stock"]:.1f} = {player_report["Actual ROP 85"]:,.0f}</span>
            <span class="cost-chip">Actual Stock Max = Actual ROP 85 + EOQ = {player_report["Final Stock Max"]:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="chart-panel"><div class="chart-title">Performance table</div>', unsafe_allow_html=True)
    st.markdown(render_report_table(report_summary), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown('<div class="chart-panel"><div class="chart-title">Average stock and pipeline</div>', unsafe_allow_html=True)
        stock_pipeline_chart = make_metric_bar_chart(
            report_summary,
            ["Average Stock", "Average Pipeline"],
            {"Average Stock": "#7bc6ff", "Average Pipeline": "#126ac7"},
            "Average units",
        )
        st.altair_chart(stock_pipeline_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with chart_col2:
        st.markdown('<div class="chart-panel"><div class="chart-title">Cost comparison</div>', unsafe_allow_html=True)
        cost_chart = make_metric_bar_chart(
            report_summary,
            ["Inventory Cost", "Backlog Cost", "Supplier Agreement Cost", "Air Freight Cost"],
            {
                "Inventory Cost": "#ff3b3b",
                "Backlog Cost": "#2684ff",
                "Supplier Agreement Cost": "#ffdf6b",
                "Air Freight Cost": "#a982ff",
            },
            "Cost",
        )
        st.altair_chart(cost_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-panel"><div class="chart-title">Fill rate achieved</div>', unsafe_allow_html=True)
    st.altair_chart(make_fill_rate_chart(report_summary), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    trend_metric = st.selectbox(
        "Monthly report chart",
        ["Cumulative Total Cost", "Ending Inventory", "Pipeline", "Ending Backlog"],
        index=0,
    )
    st.markdown('<div class="chart-panel"><div class="chart-title">Monthly trend</div>', unsafe_allow_html=True)
    st.altair_chart(make_trend_chart(report_trends, trend_metric), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    if st.session_state.variant_index == 0:
        options = second_round_options()
        if st.session_state.second_round_popup_step == "briefing" and hasattr(st, "dialog"):
            @st.dialog("Second round briefing")
            def show_second_round_briefing():
                st.markdown("## Round 2: choose a response to the shortage")
                st.markdown(
                    "You finished the first round. In the second round, the item is still the same slow-moving spare part, "
                    "and the market lead time can still jump from 1 to 3 months. Choose one mitigation strategy:"
                )
                for _, title, teaching_text, cost_text in options:
                    st.markdown(f"**{title}**")
                    st.markdown(teaching_text)
                    st.caption(cost_text)
                if st.button("Next: choose my round 2 option", type="primary", use_container_width=True):
                    st.session_state.second_round_popup_step = "choose"
                    st.rerun()

            show_second_round_briefing()

        if st.session_state.second_round_popup_step == "choose" and hasattr(st, "dialog"):
            @st.dialog("Choose round 2 option")
            def show_second_round_choice():
                st.markdown("## Select one strategy")
                st.markdown("Your choice will control the second round costs and effective lead time.")
                for variant_index, title, teaching_text, cost_text in options:
                    st.markdown(f"**{title}**")
                    st.markdown(teaching_text)
                    st.caption(cost_text)
                    if st.button(f"Choose {title}", type="primary", use_container_width=True, key=f"dialog_choose_second_{variant_index}"):
                        st.session_state.variant_index = variant_index
                        init_game()
                        st.session_state.player_ready = True
                        st.rerun()

            show_second_round_choice()

        st.markdown('<div class="section-title">Ready for Round 2?</div>', unsafe_allow_html=True)
        st.markdown("Click the button below to open a briefing popup. The next popup will let you select one of the three round 2 strategies.")
        st.markdown("""
        <div class="round-complete-card" style="margin-top:12px;">
            <div class="round-complete-title">Round 2 setup</div>
            <div class="round-complete-text">First read the strategy briefing, then choose supplier agreement or air freight.</div>
        </div>
        """, unsafe_allow_html=True)

        continue_next = st.button("Open round 2 briefing", type="primary", use_container_width=True)

        if continue_next:
            st.session_state.second_round_popup_step = "briefing" if hasattr(st, "dialog") else "inline"
            st.rerun()

        if st.session_state.second_round_popup_step == "inline":
            st.markdown('<div class="section-title">Choose Second Round Strategy</div>', unsafe_allow_html=True)
            option_cols = st.columns(3)
            for col, (variant_index, title, teaching_text, cost_text) in zip(option_cols, options):
                with col:
                    st.markdown(f"""
                    <div class="round-complete-card" style="min-height:180px;">
                        <div class="round-complete-title">{title}</div>
                        <div class="round-complete-text">{teaching_text}</div>
                        <div class="round-complete-text" style="margin-top:8px;">{cost_text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Choose {title}", type="primary", use_container_width=True, key=f"inline_choose_second_{variant_index}"):
                        st.session_state.variant_index = variant_index
                        init_game()
                        st.session_state.player_ready = True
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

        if continue_next:
            st.session_state.variant_index += 1
            init_game()
            st.session_state.player_ready = True
            st.rerun()
    else:
        st.markdown('<div class="section-title">Game completed</div>', unsafe_allow_html=True)
        st.markdown("You have completed the original slow-moving first round and your selected second-round strategy.")
        if st.session_state.completed_reports:
            completed_df = pd.DataFrame(st.session_state.completed_reports)
            if "Round" not in completed_df.columns:
                completed_df["Round"] = [f"Round {idx + 1}" for idx in range(len(completed_df))]
            comparison_cols = ["Round", "Scenario", "Cost Strategy", "Average Stock", "Total Penalty", "Fill Rate"]
            comparison_table = completed_df[[col for col in comparison_cols if col in completed_df.columns]].rename(
                columns={"Total Penalty": "Penalty Points"}
            )
            st.markdown('<div class="chart-panel"><div class="chart-title">Round 1 vs Round 2 comparison</div>', unsafe_allow_html=True)
            st.altair_chart(make_round_comparison_chart(completed_df), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-panel"><div class="chart-title">Round comparison table</div>', unsafe_allow_html=True)
            st.dataframe(comparison_table, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
            display_cols = [
                "Round",
                "Scenario",
                "Average Stock",
                "Average Pipeline",
                "Inventory Cost",
                "Backlog Cost",
                "Supplier Agreement Cost",
                "Air Freight Cost",
                "Total Cost",
                "Cost Points",
                "Fill Rate",
                "Fill Rate Penalty",
                "Actual End Lead Time",
                "Actual ROP 85",
                "Final Stock Max",
                "Excess Inventory Units",
                "Overstock Penalty",
                "Total Penalty",
            ]
            st.dataframe(completed_df[[col for col in display_cols if col in completed_df.columns]], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# SECTION 12C: INVENTORY POSITION VS ROP GRAPH
# =========================================================

if st.session_state.history:
    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Inventory Position vs ROP</div>', unsafe_allow_html=True)
    inventory_rop_chart = build_inventory_position_rop_svg()
    html(inventory_rop_chart, height=190)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# SECTION 13: TABLE
# =========================================================

if st.session_state.history:
    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Month-by-month table</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, height=420)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# SECTION 14: GRAPH
# =========================================================

if st.session_state.history:
    chart_df = pd.DataFrame(st.session_state.history).set_index("Month")

    st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Trends</div>', unsafe_allow_html=True)
    st.line_chart(chart_df[[
        "Ending Inventory",
        "Ending Backlog",
        "Pipeline",
        "Inventory Position After Order",
        "Total Customer Need"
    ]])
    st.markdown('</div>', unsafe_allow_html=True)
