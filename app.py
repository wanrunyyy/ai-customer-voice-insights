"""AI Voice of Customer | colorful Streamlit portfolio dashboard.

Run from the project folder:
    python -m streamlit run app.py

Requires only the project's existing dependencies: pandas and streamlit
(Altair ships with Streamlit).
"""

from pathlib import Path
from html import escape
import json

import altair as alt
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

st.set_page_config(
    page_title="AI Voice of Customer | Insight Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----- Visual design: colorful but readable; no images, fonts or extra packages. -----
st.markdown(
    """
<style>
:root { --ink:#17213c; --muted:#71809b; --violet:#6757e8; --blue:#3c8df5; }
.stApp {
    background: radial-gradient(circle at 90% 4%, #f5ecff 0, transparent 32%),
                radial-gradient(circle at 0 20%, #ecf8ff 0, transparent 36%),
                #f8faff;
    color: var(--ink);
}
.block-container { padding-top:2.1rem; padding-bottom:2.5rem; max-width:1330px; }
[data-testid="stHeader"] { background: transparent; }
h1,h2,h3 { color:#192442 !important; letter-spacing:-.025em; }
h1 { font-weight:800 !important; }
[data-testid="stVerticalBlock"] { gap: .85rem; }
.hero {
    position:relative; overflow:hidden; border-radius:25px;
    padding:36px 41px 32px; color:white; margin-bottom:20px;
    background: linear-gradient(118deg, #574ad8 0%, #7460e8 43%, #bb6bd9 76%, #f28aa0 100%);
    box-shadow:0 14px 36px rgba(104,89,215,.22);
}
.hero::before, .hero::after { content:""; position:absolute; border-radius:50%; pointer-events:none; }
.hero::before { width:290px;height:290px;right:-80px;top:-160px;background:rgba(255,255,255,.13); }
.hero::after { width:145px;height:145px;right:200px;bottom:-116px;background:rgba(255,255,255,.10); }
.hero-kicker { text-transform:uppercase; letter-spacing:.18em; font-size:11px; font-weight:800; color:#ece6ff; }
.hero h1 { margin:10px 0 6px; color:white !important; font-size:37px; font-weight:850; }
.hero p { margin:0 0 20px; color:#f6f0ff; font-size:15px; }
.hero-tags { display:flex;gap:8px;flex-wrap:wrap; }
.hero-tags span { padding:7px 11px; border-radius:99px; background:rgba(255,255,255,.18);
    border:1px solid rgba(255,255,255,.26); color:white; font-size:12px; font-weight:600; }
.note { border-radius:13px; background:#eeedff; border:1px solid #dedbff;
    color:#504db4; padding:11px 16px; font-size:13px; margin:4px 0 17px; }
.metric-card {
    background:white; border-radius:18px; border:1px solid #e8ebf7;
    padding:19px 20px 18px; min-height:125px;
    box-shadow:0 7px 22px rgba(32,40,95,.055); position:relative; overflow:hidden;
}
.metric-card::before {content:"";position:absolute;left:0;top:0;width:100%;height:5px;background:var(--accent);}
.metric-head { display:flex;align-items:center;justify-content:space-between; }
.metric-label {font-size:13px;font-weight:650;color:#6b7790;}
.metric-icon { font-size:20px; }
.metric-value {font-size:31px;line-height:1.15;font-weight:840;letter-spacing:-.035em;color:#18233f;margin-top:16px;}
.metric-sub {color:#8792a6;font-size:11px;margin-top:6px;}
.section-intro {margin:21px 0 14px;}
.section-kicker {font-size:11px;letter-spacing:.15em;font-weight:800;color:#7c68e7;text-transform:uppercase;}
.section-title {font-size:23px;font-weight:820;color:#1e2842;margin:5px 0 5px;}
.section-desc {font-size:13px;color:#76829a;}
[data-baseweb="tab-list"] { gap:9px !important; margin-top:20px; margin-bottom:11px; padding-bottom:10px; }
button[data-baseweb="tab"] {
    border-radius:13px !important; padding:11px 17px !important;
    background:white !important; border:1px solid #e7e9f5 !important;
    box-shadow:0 2px 8px rgba(20,30,60,.035); height:auto !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background:#f0edff !important; color:#574bd7 !important; border-color:#bfb6ff !important;
}
[data-baseweb="tab-highlight"] { background-color:#7662ea !important; }
[data-testid="stAltairChart"] { background:white; border:1px solid #e8ebf6;
    box-shadow:0 5px 22px rgba(36,45,90,.035); padding:13px 14px 4px; border-radius:18px; }
[data-testid="stDataFrame"] {border-radius:13px;overflow:hidden;}
[data-testid="stSelectbox"], [data-testid="stTextInput"] {border-radius:12px;}
[data-testid="stExpander"] { background:white;border-radius:15px !important;
    border:1px solid #e6e9f5 !important; box-shadow:0 3px 13px rgba(48,62,96,.035); }
[data-testid="stDownloadButton"] button {background:#6859dc;color:white;border:0;border-radius:12px;font-weight:700;}
[data-testid="stDownloadButton"] button:hover {color:white;background:#5848d3;border:0;}
.pill {display:inline-block;font-size:12px;padding:5px 10px;border-radius:99px;font-weight:750;}
.review-card {background:white;border:1px solid #e5e9f5;border-radius:18px;padding:21px 24px;
    box-shadow:0 7px 23px rgba(30,42,88,.06);margin-top:8px;}
.review-card h4 { margin:0 0 12px; font-size:18px; color:#192442; }
.review-original {font-size:14px;line-height:1.75;color:#3f4962;background:#f7f8fd;padding:13px 15px;border-radius:11px;white-space:pre-wrap;}
.review-need {background:#f2efff;color:#5149a6;border-radius:11px;padding:12px 15px;margin-top:11px;font-size:14px;}
.soft-card {background:white;border:1px solid #e8e9f6;border-radius:18px;padding:19px 20px;
    box-shadow:0 5px 20px rgba(42,52,91,.04);margin:7px 0 10px;}
.soft-kicker {color:#7b87a1;font-size:12px;font-weight:700;letter-spacing:.04em;}
.soft-number {font-size:26px;font-weight:850;margin:4px 0;color:#20294a;}
.test-card {background:white;border:1px solid #ebecf6;border-radius:15px;padding:18px;min-height:132px;}
.test-title {font-weight:800;color:#26304c;margin:7px 0;}
.test-desc {font-size:13px;color:#72809b;line-height:1.6;}
.footer {font-size:12px;color:#8790a6;padding-top:20px;border-top:1px solid #e6e9f4;margin-top:30px;}
@media(max-width:730px) {.hero{padding:27px 22px}.hero h1{font-size:29px}.metric-value{font-size:26px}}
</style>
""",
    unsafe_allow_html=True,
)


def metric_card(label, value, subtitle, color, icon):
    """Only authored labels and preformatted numeric values go into this HTML."""
    st.markdown(
        f'<div class="metric-card" style="--accent:{color}">'
        f'<div class="metric-head"><span class="metric-label">{escape(str(label))}</span>'
        f'<span class="metric-icon">{icon}</span></div>'
        f'<div class="metric-value">{escape(str(value))}</div>'
        f'<div class="metric-sub">{escape(str(subtitle))}</div></div>',
        unsafe_allow_html=True,
    )


def intro(kicker, title, desc):
    st.markdown(
        '<div class="section-intro">'
        f'<div class="section-kicker">{escape(kicker)}</div>'
        f'<div class="section-title">{escape(title)}</div>'
        f'<div class="section-desc">{escape(desc)}</div></div>',
        unsafe_allow_html=True,
    )


def colored_chart(chart, height=320):
    """Unify font, grids, tooltips, and padding across Altair charts."""
    chart = (
        chart.properties(height=height, padding={"left": 6, "right": 22, "top": 18, "bottom": 5})
        .configure_view(stroke=None)
        .configure_axis(
            labelColor="#6b7793", titleColor="#66728b", labelFontSize=12,
            titleFontSize=12, gridColor="#edf0f8", tickColor="#dfe4f0",
            domain=False, labelPadding=9,
        )
        .configure_legend(labelColor="#6b7793", titleColor="#66728b", labelFontSize=12, symbolSize=100)
    )
    st.altair_chart(chart, use_container_width=True)


st.markdown(
    """
<div class="hero">
  <div class="hero-kicker">✨ AI / VOICE OF CUSTOMER / INSIGHT STUDIO</div>
  <h1>让用户的声音，变成商业洞察。</h1>
  <p>AI Voice of Customer · 真实电商评论分析与产品、运营、市场决策支持</p>
  <div class="hero-tags">
    <span>✦ LLM 文本理解</span><span>◈ 用户痛点洞察</span>
    <span>◎ 可追溯原始证据</span><span>↗ 商业假设验证</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

path = DATA / "enriched_reviews.csv"
summary_path = DATA / "full_summary.json"
if not path.exists() or not summary_path.exists():
    st.warning("尚未生成分析结果。请先运行 prepare_data.py → AI 分类 → validate_labels.py。")
    st.stop()

review = pd.read_csv(path, dtype={"review_id": str}).fillna("")
summary = json.loads(summary_path.read_text(encoding="utf-8"))
review["rating"] = pd.to_numeric(review["rating"], errors="coerce")
for col in ["topic", "sentiment", "department_name", "review_text", "user_need"]:
    if col not in review.columns:
        st.error(f"数据缺少字段：{col}。请检查 data/enriched_reviews.csv。")
        st.stop()

st.markdown(
    '<div class="note">ⓘ 历史匿名化公开评论。完整有效数据用于评分基线；AI 样本刻意抽取低评分 100 条＋高评分 100 条，'
    '样本情绪和主题比例不能外推至全部用户。所有业务建议均为待验证的假设。</div>',
    unsafe_allow_html=True,
)

cols = st.columns(4, gap="medium")
with cols[0]:
    metric_card("原始评论记录", f'{summary["n_original_rows"]:,}', "Kaggle 公开数据", "#6d5ff0", "🗂️")
with cols[1]:
    metric_card("有效非重复评论", f'{summary["n_clean_unique_reviews"]:,}', "清洗后的评分基线", "#2db7b0", "✓")
with cols[2]:
    metric_card("完整数据平均评分", f'{summary["mean_rating"]:.2f} / 5', "不是定向样本平均分", "#f4a548", "★")
with cols[3]:
    metric_card("AI 深度分类", f"{len(review):,}", "真实评论 · 定向抽样", "#ee76a7", "✦")

base, pain, feedback, action = st.tabs(
    ["📊 评分基线", "🔍 AI 痛点主题", "🧾 原始证据", "💡 商业建议"]
)

# ----- Tab 1: full dataset population-eligible baseline stats -----
with base:
    intro("01 / THE BIG PICTURE", "完整数据评分概况", "先看全部有效评论的评分情况，再解读定向抽取的 AI 样本。")
    dist = pd.DataFrame(
        [{"评分": f"{int(k)}星", "评论数": int(v), "order": int(k)}
         for k, v in summary["rating_distribution"].items()]
    ).sort_values("order")
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.markdown("**⭐ 用户评分分布**")
        rating_order = [f"{i}星" for i in range(1, 6)]
        rating_colors = ["#ef758d", "#f69f72", "#f8c96c", "#65c9b4", "#637de9"]
        chart = alt.Chart(dist).mark_bar(cornerRadiusTopLeft=7, cornerRadiusTopRight=7, size=48).encode(
            x=alt.X("评分:N", sort=rating_order, title=None,
                    axis=alt.Axis(labelAngle=0, labelFontSize=13)),
            y=alt.Y("评论数:Q", title="评论数", axis=alt.Axis(format=",.0f")),
            color=alt.Color("评分:N", scale=alt.Scale(domain=rating_order, range=rating_colors), legend=None),
            tooltip=["评分:N", alt.Tooltip("评论数:Q", format=",.0f")],
        )
        colored_chart(chart, height=320)
    with right:
        st.markdown("**🍃 低评分占比（1–3 星）**")
        low_share = float(summary["lower_rating_share"])
        n_total = int(summary["n_clean_unique_reviews"])
        n_low = int(summary.get("n_lower_rating", round(n_total * low_share)))
        share_df = pd.DataFrame(
            [{"类型": "1–3星", "数量": n_low}, {"类型": "4–5星", "数量": max(n_total - n_low, 0)}]
        )
        donut = alt.Chart(share_df).mark_arc(innerRadius=78, outerRadius=116).encode(
            theta=alt.Theta("数量:Q"),
            color=alt.Color("类型:N", scale=alt.Scale(domain=["1–3星", "4–5星"], range=["#ff8c98", "#6e78e9"]), title=None),
            tooltip=["类型:N", alt.Tooltip("数量:Q", format=",.0f")],
        )
        colored_chart(donut, height=263)
        st.markdown(f'**{low_share:.1%}** 的有效评论为 1–3 星（{n_low:,} 条）')
    st.caption("数据基线来自清洗、去重后的完整有效评论；与刻意平衡高低评分的 200 条 AI 样本分开统计。")

# ----- Tab 2: AI diagnostic sample -----
with pain:
    intro("02 / DISCOVER THE PATTERNS", "AI 主题与情绪洞察", "按商品类别筛选，分别查看话题覆盖量、明确负面反馈与混合反馈。")
    department_options = ["全部"] + sorted(review["department_name"].astype(str).unique().tolist())
    selected_department = st.selectbox("商品类别", department_options, key="pain_dept")
    subset = review if selected_department == "全部" else review[review.department_name == selected_department]
    total_n = len(subset)
    negative_n = int((subset.sentiment == "负面").sum())
    mixed_n = int((subset.sentiment == "中性/混合").sum())
    cc = st.columns(3)
    with cc[0]: metric_card("当前筛选评论", f"{total_n}", "定向样本数量", "#6b59eb", "◉")
    with cc[1]: metric_card("明确负面", f"{negative_n}", "与混合评价分开统计", "#f77c89", "↘")
    with cc[2]: metric_card("中性／混合", f"{mixed_n}", "不直接等同于投诉", "#f5b258", "◐")
    st.caption("当前图表只描述定向样本，不能用于估计完整电商评论的主题分布。")
    lcol, rcol = st.columns([1, 1.15], gap="large")
    with lcol:
        st.markdown("**🌈 反馈主题热度排行**")
        counts = subset.topic.value_counts().rename_axis("主题").reset_index(name="数量")
        if not counts.empty:
            bar = alt.Chart(counts).mark_bar(cornerRadiusEnd=7, size=23).encode(
                x=alt.X("数量:Q", title="评论条数", axis=alt.Axis(format="d")),
                y=alt.Y("主题:N", sort="-x", title=None),
                color=alt.Color("主题:N", legend=None,
                    scale=alt.Scale(domain=["尺码与版型", "款式与外观", "面料与质量", "价格与价值感", "物流与服务", "其他"],
                                    range=["#7168ed", "#f69a6b", "#43bdb5", "#ecc665", "#6a99e9", "#b9a4d9"])),
                tooltip=["主题:N", "数量:Q"],
            )
            colored_chart(bar, height=310)
        else:
            st.info("当前筛选条件下没有评论。")
    with rcol:
        st.markdown("**🎨 每个主题的情绪构成**")
        if total_n:
            grouped = subset.groupby(["topic", "sentiment"], dropna=False).size().reset_index(name="数量")
            stacked = alt.Chart(grouped).mark_bar(cornerRadiusEnd=3).encode(
                x=alt.X("数量:Q", title="评论条数", axis=alt.Axis(format="d")),
                y=alt.Y("topic:N", sort=counts["主题"].tolist(), title=None),
                color=alt.Color("sentiment:N", title="情绪", scale=alt.Scale(
                    domain=["正面", "中性/混合", "负面"],
                    range=["#48bdad", "#f1c36c", "#ed778b"])),
                tooltip=[alt.Tooltip("topic:N", title="主题"), alt.Tooltip("sentiment:N", title="情绪"), "数量:Q"],
            )
            colored_chart(stacked, height=310)
        else:
            st.info("当前筛选条件下没有评论。")
    st.markdown("**📋 主题 × 情绪明细**")
    if total_n:
        table = pd.crosstab(subset.topic, subset.sentiment).reindex(
            columns=["正面", "中性/混合", "负面"], fill_value=0
        )
        table["总计"] = table.sum(axis=1)
        table["明确负面占比（样本内）"] = (table["负面"] / table["总计"]).map(lambda n: f"{n:.1%}")
        table = table.sort_values("总计", ascending=False)
        st.dataframe(table, use_container_width=True)

# ----- Tab 3: traceable original text evidence -----
with feedback:
    intro("03 / FOLLOW THE EVIDENCE", "每条洞察，都能追溯到原始评论", "组合筛选评论；选择一条记录，查看完整英文反馈与 AI 的中文摘要。")
    f1, f2, f3 = st.columns(3)
    with f1:
        selected_sentiment = st.selectbox("情绪", ["全部", "正面", "负面", "中性/混合"], key="evidence_sentiment")
    with f2:
        selected_topic = st.selectbox("主题", ["全部"] + sorted(review.topic.unique().tolist()), key="evidence_topic")
    with f3:
        selected_dep = st.selectbox("商品类别", department_options, key="evidence_department")
    keyword = st.text_input("🔎 搜索评论 ID / 原文关键词", placeholder="例如 R0009、fabric、size", key="evidence_search")
    show = review.copy()
    if selected_sentiment != "全部":
        show = show[show.sentiment == selected_sentiment]
    if selected_topic != "全部":
        show = show[show.topic == selected_topic]
    if selected_dep != "全部":
        show = show[show.department_name == selected_dep]
    if keyword.strip():
        kw = keyword.strip()
        matched = show.review_id.str.contains(kw, case=False, regex=False, na=False)
        matched |= show.review_text.str.contains(kw, case=False, regex=False, na=False)
        show = show[matched]
    st.caption(f"匹配 {len(show)} / {len(review)} 条定向样本评论 · 表格支持排序和滚动")
    visible_cols = ["review_id", "rating", "department_name", "sentiment", "topic", "user_need", "review_text"]
    if not show.empty:
        st.dataframe(
            show[visible_cols], use_container_width=True, hide_index=True, height=305,
            column_config={
                "review_id": st.column_config.TextColumn("ID", width="small"),
                "rating": st.column_config.NumberColumn("星级", format="%d ⭐", width="small"),
                "department_name": st.column_config.TextColumn("商品类别", width="small"),
                "sentiment": st.column_config.TextColumn("情绪", width="small"),
                "topic": st.column_config.TextColumn("主题", width="medium"),
                "user_need": st.column_config.TextColumn("用户需求摘要", width="large"),
                "review_text": st.column_config.TextColumn("英文原文", width="large"),
            },
        )
        st.download_button(
            "⬇ 下载当前筛选结果 CSV",
            data=show.to_csv(index=False).encode("utf-8-sig"),
            file_name="selected_reviews.csv", mime="text/csv",
        )
        chosen = st.selectbox("选择评论，展开完整内容", show.review_id.astype(str).tolist(), key="evidence_id")
        item = show.loc[show.review_id.astype(str) == chosen].iloc[0]
        tone = {"正面": ("#dbf7ee", "#178875"), "负面": ("#ffedf0", "#c44a6a"),
                "中性/混合": ("#fff2d9", "#af8126")}.get(item.sentiment, ("#f0f0fa", "#6b7291"))
        stars = int(item.rating) if pd.notna(item.rating) else "—"
        st.markdown(
            '<div class="review-card">'
            f'<h4>📄 {escape(str(item.review_id))} · {escape(str(stars))} 星 · {escape(str(item.department_name))}</h4>'
            f'<span class="pill" style="background:{tone[0]};color:{tone[1]}">{escape(str(item.sentiment))}</span> '
            f'<span class="pill" style="background:#eeeafd;color:#6854bd">{escape(str(item.topic))}</span>'
            '<p style="margin:17px 0 8px;font-weight:750;color:#303b59">原始英文评论</p>'
            f'<div class="review-original">{escape(str(item.review_text))}</div>'
            f'<div class="review-need"><b>✦ AI 提取的用户需求</b>　{escape(str(item.user_need))}</div>'
            '</div>', unsafe_allow_html=True,
        )
    else:
        st.info("没有符合条件的评论。请尝试清除关键词或调整筛选条件。")

# ----- Tab 4: action hypotheses, not causal proof or measured uplift -----
with action:
    intro("04 / FROM INSIGHT TO ACTION", "从分析结果，到值得验证的业务假设", "分别为产品、运营、市场提出可测试的行动；并不意味着已带来实际增长。")
    proposals = {
        "尺码与版型": ["产品｜优化尺码指引并测试尺码推荐", "运营｜完善换码 FAQ 和咨询话术", "市场｜用不同身材的真实试穿辅助表达"],
        "面料与质量": ["产品｜整理质量异常并建立质检检查表", "运营｜明确材质、洗护与退换说明", "市场｜使用经核实的材质信息，减少预期偏差"],
        "款式与外观": ["产品｜检查商品图片和实物的一致性", "运营｜收集不同场景的穿搭体验", "市场｜测试更清晰的模特上身展示"],
        "价格与价值感": ["产品｜核对功能价值与价格定位", "运营｜整理用户对价格的疑问", "市场｜测试能证明价值的卖点表达"],
        "物流与服务": ["产品｜检查售后流程和使用障碍", "运营｜整理配送与退换咨询路径", "市场｜避免未经核实的时效承诺"],
        "其他": ["产品｜扩展主题标签并人工复核", "运营｜记录并跟进新的反馈类型", "市场｜暂不依据零散反馈下结论"],
    }
    issue_df = review[review.sentiment.isin(["负面", "中性/混合"])]
    priority = issue_df.topic.value_counts().head(3)
    pos_topics = review.loc[review.sentiment == "正面", "topic"].value_counts()
    positive_topic = pos_topics.index[0] if len(pos_topics) else "暂无"
    top_negative = review.loc[review.sentiment == "负面", "topic"].value_counts()
    first_negative = top_negative.index[0] if len(top_negative) else "暂无"
    m1, m2, m3 = st.columns(3)
    with m1: metric_card("最常出现的待调查主题", priority.index[0] if len(priority) else "暂无", "负面＋中性／混合样本", "#6c64ee", "🔎")
    with m2: metric_card("明确负面主要话题", first_negative, "仅按明确负面评论统计", "#f48292", "⚠")
    with m3: metric_card("正面反馈突出主题", positive_topic, "可进一步探索营销素材", "#43c1aa", "✨")
    st.markdown("**🎯 候选改进机会：先观察，再验证**")
    for idx, (topic_name, n) in enumerate(priority.items(), start=1):
        sub = issue_df[issue_df.topic == topic_name]
        negative_count = int((sub.sentiment == "负面").sum())
        mixed_count = int((sub.sentiment == "中性/混合").sum())
        with st.expander(
            f"#{idx}　{topic_name}　｜明确负面 {negative_count} · 中性／混合 {mixed_count}",
            expanded=(idx == 1),
        ):
            st.caption(f"本类共有 {n} 条待调查反馈；包含中性／混合评论，不等于 {n} 条投诉。")
            for line in proposals.get(topic_name, proposals["其他"]):
                st.write("• " + line)
            evidence = sub.head(2)
            if not evidence.empty:
                st.caption("可追溯评论 ID：" + "、".join(evidence.review_id.astype(str).tolist()))
            st.caption("排序仅按样本中出现次数生成；未纳入影响范围、改进成本、可行性，不代表最终业务优先级。")
    st.markdown("**🧪 如何衡量这些建议是否有效？**")
    t1, t2, t3 = st.columns(3)
    for c, icon, name, msg in [
        (t1, "🧩", "产品验证", "小规模可用性测试：尺码选择成功率、任务完成率、用户理解程度。"),
        (t2, "💬", "运营验证", "FAQ 小流量测试：问题解决率、重复咨询率、退换咨询体验。"),
        (t3, "📣", "市场验证", "基于真实正面反馈制作两版素材，比较点击率与转化表现。"),
    ]:
        with c:
            st.markdown(
                '<div class="test-card">'
                f'<div style="font-size:23px">{icon}</div><div class="test-title">{name}</div>'
                f'<div class="test-desc">{escape(msg)}</div></div>',
                unsafe_allow_html=True,
            )
    checked = DATA / "manual_check.csv"
    if checked.exists():
        a = pd.read_csv(checked, dtype=str).fillna("")
        needed_cols = {"manual_sentiment", "manual_topic", "ai_sentiment", "ai_topic"}
        if needed_cols.issubset(a.columns):
            verified = a[(a.manual_sentiment.str.strip() != "") & (a.manual_topic.str.strip() != "")].copy()
            if len(verified):
                sent_agreement = (verified.ai_sentiment.str.strip() == verified.manual_sentiment.str.strip()).mean()
                topic_agreement = (verified.ai_topic.str.strip() == verified.manual_topic.str.strip()).mean()
                st.markdown("**✅ AI 分类质量：人工复核**")
                q1, q2, q3 = st.columns(3)
                with q1: metric_card("已复核", f"{len(verified)} 条", "仅人工复核子样本", "#8675ea", "👤")
                with q2: metric_card("情绪一致率", f"{sent_agreement:.1%}", "AI 与人工标签一致", "#36baaa", "✓")
                with q3: metric_card("主题一致率", f"{topic_agreement:.1%}", "AI 与人工标签一致", "#faab67", "◎")
                st.caption("这是人工复核样本的一致率，不代表全部评论上的真实准确率；复核过程中存在少量共同讨论的案例。")
            else:
                st.info("人工复核表已存在，但尚未填写复核结果。")

st.markdown(
    '<div class="footer">Data source: Kaggle · Women’s E-Commerce Clothing Reviews (historical anonymized public data, CC0). '
    'AI-assisted descriptive analysis · not a deployed commercial service · business impact has not been measured.</div>',
    unsafe_allow_html=True,
)
