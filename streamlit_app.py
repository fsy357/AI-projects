import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import datetime
import os

# 强制编码，解决Windows报错
os.environ["PYTHONIOENCODING"] = "utf-8"

# ==========================
# 会话状态初始化
# ==========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "result_text" not in st.session_state:
    st.session_state.result_text = ""
if "book_outline" not in st.session_state:
    st.session_state.book_outline = ""

# ==========================
# 页面配置 + 莫兰迪高级配色
# ==========================
st.set_page_config(page_title="网文+短剧AI生成器", layout="wide", page_icon="✍️")

morandi_css = """
<style>
.stApp { background: #F8F5F2; }
.block-container { padding: 1.5rem 2rem; max-width: 1400px; margin: 0 auto; }
[data-testid="stColumn"] > div > div { background: #F3EAE5; border-radius: 16px; padding: 22px 24px; box-shadow: 0 3px 10px #E6E0DC; }
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div { background: #F0E9E5; border: 1px solid #DCD3CE; }
.stButton>button { background: #A9B6B2; color: #222; border: none; border-radius: 10px; }
.stButton>button:hover { background: #8B9B97; color: white; }
h1, h2, h3 { color: #5C5753; }
#MainMenu, footer, header { display: none; }
</style>
"""
st.markdown(morandi_css, unsafe_allow_html=True)

# ==========================
# 标题
# ==========================
st.markdown("<h1 style='text-align:center; margin-bottom:10px;'>✍️ 网文 + 短剧剧本 双模式 AI 生成器</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#777'>支持：大纲生成 | 章节写作 | 短剧剧本 | 拆书仿写 | 爽点自动创作 | 对话续稿</p>", unsafe_allow_html=True)
st.divider()

# ==========================
# 核心左右布局：左设置 + 右生成
# ==========================
left_bar, right_area = st.columns([0.35, 0.65])

# --------------------------
# 左侧：配置面板（API + 模式 + 输入）
# --------------------------
with left_bar:
    st.subheader("⚙️ 全局设置")
    # API KEY（界面输入，不上传代码）
    api_key = st.text_input("🔐 DeepSeek / OpenAI API Key", type="password", placeholder="在这输入你的Key，代码不保存")
    api_base = st.text_input("API 地址", value="https://api.deepseek.com/v1")

    # 创作温度
    temperature = st.slider("创意强度", 0.1, 1.5, 0.7, 0.1)

    st.divider()
    st.subheader("📝 创作模式")
    mode = st.selectbox("选择生成模式", [
        "📖 网文生成（大纲→分卷→章节）",
        "🎬 短剧剧本（30秒/3分钟 台词+分镜）",
        "✍️ 智能拆书仿写（防重复）"
    ])

    st.divider()
    st.subheader("📌 输入创作信息")
    novel_theme = st.text_input("小说/短剧题材", placeholder="例如：重生、都市、战神、甜宠、复仇")
    novel_hot = st.text_input("爽点/关键词", placeholder="例如：打脸、逆袭、反转、暴富、霸总")

    # 不同模式显示不同输入框
    user_input = ""
    if mode == "📖 网文生成（大纲→分卷→章节）":
        book_part = st.selectbox("生成内容", ["全书大纲", "分卷剧情", "单章正文"])
        user_input = st.text_area("补充要求", height=100, placeholder="例如：写第三章，节奏紧凑，爽点密集",key="inp1")

    elif mode == "🎬 短剧剧本（30秒/3分钟 台词+分镜）":
        script_len = st.selectbox("剧本时长", ["30秒（短视频）", "3分钟（抖音短剧）"])
        user_input = st.text_area("剧情梗概", height=100, placeholder="例如：女主被甩后当场变身集团总裁",key="inp2")

    elif mode == "✍️ 智能拆书仿写（防重复）":
        user_input = st.text_area("粘贴热门小说片段", height=160, placeholder="粘贴你要仿写的热门小说段落",key="inp3")

    # 生成按钮
    st.divider()
    if st.button("🚀 开始生成", type="primary", use_container_width=True):
        if not api_key:
            st.error("请先输入 API Key！")
        else:
            with st.spinner("AI 创作中..."):
                llm = ChatOpenAI(
                    model="deepseek-chat",
                    api_key=api_key.strip(),
                    base_url=api_base,
                    temperature=temperature
                )

                # 不同模式提示词
                if mode == "📖 网文生成（大纲→分卷→章节）":
                    prompt = f"""你是顶级网文作者，写爆款爽文。
题材：{novel_theme}，爽点：{novel_hot}
生成：{book_part}
要求：节奏快、爽点足、符合番茄/七猫风格。
用户要求：{user_input}"""

                elif mode == "🎬 短剧剧本（30秒/3分钟 台词+分镜）":
                    prompt = f"""你是抖音爆款短剧编剧，写{script_len}剧本。
题材：{novel_theme}，爽点：{novel_hot}
格式：分镜+台词+场景，口语化、强冲突、高反转。
剧情：{user_input}"""

                else:
                    prompt = f"""你是智能仿写专家，仿写同套路但不抄袭。
原文段落：{user_input}
题材：{novel_theme}，爽点：{novel_hot}
要求：保留核心爽点，更换人物、剧情、措辞，原创度高，可直接发布。"""

                # 生成
                res = llm.invoke(prompt)
                st.session_state.result_text = res.content
                st.session_state.messages.append(HumanMessage(content=f"生成：{mode}：{user_input}"))
                st.session_state.messages.append(AIMessage(content=res.content))
                st.success("生成完成！→ 右侧查看")

# --------------------------
# 右侧：生成结果 + 聊天续稿
# --------------------------
with right_area:
    st.subheader("📄 生成结果")
    st.text_area("最终内容", st.session_state.result_text, height=320, key="result_box")

    # 下载+清空按钮
    c1, c2 = st.columns(2)
    with c1:
        if st.session_state.result_text:
            # 修复datetime报错：datetime.datetime.now
            st.download_button("💾 下载 TXT", st.session_state.result_text,
                               file_name=f"AI创作_{datetime.datetime.now().strftime('%m%d%H%M')}.txt", use_container_width=True)
    with c2:
        if st.button("🔄 清空内容", use_container_width=True):
            st.session_state.result_text = ""
            st.session_state.messages = []

    st.divider()
    st.subheader("💬 对话续稿区（输入指令续写/改稿）")
    # 新增聊天输入框，用来续第二章、改剧情
    chat_input = st.chat_input("输入指令：续写第二章正文、修改主角人设、重写上一章...")
    if chat_input and api_key:
        st.session_state.messages.append(HumanMessage(content=chat_input))
        with st.chat_message("user",avatar="👤"):
            st.markdown(chat_input)
        with st.chat_message("assistant",avatar="🤖"):
            with st.spinner("正在修改/续写..."):
                llm = ChatOpenAI(model="deepseek-chat",api_key=api_key.strip(),base_url=api_base,temperature=temperature)
                prompt = f"""基于已有全文内容：{st.session_state.result_text}，题材{novel_theme}，爽点{novel_hot}，按照用户指令修改或续写内容；网文保持番茄爽文风、短剧保持短视频口语分镜。用户指令：{chat_input}"""
                resp = llm.invoke(prompt)
                ai_txt = resp.content
                st.markdown(ai_txt)
                st.session_state.messages.append(AIMessage(content=ai_txt))
                # 续写自动拼接进正文
                if "第" in ai_txt and "章" in ai_txt:
                    st.session_state.result_text += f"\n\n{ai_txt}"

    # 历史对话展示
    st.divider()
    st.subheader("📜 创作历史记录")
    chat_container = st.container(height=220)
    with chat_container:
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                st.chat_message("user", avatar="📝").write(msg.content)
            else:
                st.chat_message("assistant", avatar="🤖").write(msg.content)
