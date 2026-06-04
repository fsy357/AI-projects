import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import datetime
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

st.set_page_config(page_title="网文+短剧AI生成器", layout="wide", page_icon="📝")

css = """
<style>
.block-container { padding:0.5rem 0.8rem !important; max-width:100% !important; }
section[data-testid="stSidebar"] { padding-top:0px !important; padding-bottom:0px !important; }
section[data-testid="stSidebar"] > div { padding:0 !important; }
[data-testid="stColumn"]:first-child > div > div {background:#b4cfc2;border-radius:14px;padding:12px 14px;box-shadow:0 2px 5px rgba(180,207,194,0.3);margin-bottom:0.6rem;}
[data-testid="stColumn"]:nth-child(2) > div > div {background:#92b8a7;border-radius:14px;padding:12px 14px;box-shadow:0 2px 5px rgba(146,184,167,0.3);margin-bottom:0.6rem;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stSelectbox>div>div{background:#d1e4dd;border:1px solid #b4cfc2;}
.stButton>button{background:#5a8272;color:#fff;border:none;border-radius:9px;}
.stButton>button:hover{background:#4a7162;}
h1,h2,h3{color:#3a504a;margin:0.3rem 0 0.5rem 0;}
#MainMenu,footer,header{display:none;}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

if "result_text" not in st.session_state:
    st.session_state.result_text = ""

st.markdown("<h1 style='text-align:center;margin:5px 0;'>📝 网文 + 短剧剧本 双模式 AI 生成器</h1>",unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#3a504a;margin-bottom:8px;'>支持：大纲生成 | 章节写作 | 短剧剧本 | 拆书仿写 | 对话续稿</p>",unsafe_allow_html=True)
st.divider()

left_bar, right_area = st.columns([0.35, 0.65])

with left_bar:
    st.subheader("⚙️ 全局设置")
    api_key = st.text_input("🔐 DeepSeek / OpenAI API Key", type="password", placeholder="填入个人密钥，仅网页临时生效")
    api_base = st.text_input("API 地址", value="https://api.deepseek.com/v1")
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

    user_input = ""
    if mode == "📖 网文生成（大纲→分卷→章节）":
        book_part = st.selectbox("生成内容", ["全书大纲", "分卷剧情", "单章正文"])
        user_input = st.text_area("补充要求", height=70, placeholder="例如：写第三章，节奏紧凑，爽点密集", key="inp1")
    elif mode == "🎬 短剧剧本（30秒/3分钟 台词+分镜）":
        script_len = st.selectbox("剧本时长", ["30秒（短视频）", "3分钟（抖音短剧）"])
        user_input = st.text_area("剧情梗概", height=70, placeholder="例如：女主被甩后当场变身集团总裁", key="inp2")
    elif mode == "✍️ 智能拆书仿写（防重复）":
        user_input = st.text_area("粘贴热门小说片段", height=110, placeholder="粘贴你要仿写的热门小说段落", key="inp3")

    st.divider()
    if st.button("🚀 开始生成", type="primary", use_container_width=True):
        if not api_key:
            st.error("请先输入 API Key！")
        else:
            with st.spinner("AI 创作中..."):
                llm = ChatOpenAI(model="deepseek-chat", api_key=api_key.strip(), base_url=api_base, temperature=temperature)
                if mode == "📖 网文生成（大纲→分卷→章节）":
                    prompt = f"""网文爽文风格，题材{novel_theme}，爽点{novel_hot}，生成{book_part}，用户需求：{user_input}"""
                elif mode == "🎬 短剧剧本（30秒/3分钟 台词+分镜）":
                    prompt = f"""严格【场景｜镜头+角色：台词】短剧格式，禁止小说段落，{script_len}，题材{novel_theme}，爽点{novel_hot}，剧情：{user_input}
【场景：咖啡馆｜近景】
女主：你凭什么耍无赖。"""
                else:
                    prompt = f"""原文仿写不抄袭，原文：{user_input}，题材{novel_theme}，爽点{novel_hot}"""
                res = llm.invoke(prompt)
                content = res.content
                st.session_state.result_text = content
            st.rerun()

with right_area:
    st.subheader("📄 生成结果")
    # 关键：改用markdown渲染内容，不会出现渲染空白BUG
    if st.session_state.result_text.strip():
        st.markdown(st.session_state.result_text)
    else:
        st.info("暂无内容，点击左侧开始生成")

    c1,c2 = st.columns(2)
    with c1:
        if st.session_state.result_text.strip():
            st.download_button("💾 下载 TXT", st.session_state.result_text,
                               file_name=f"AI创作_{datetime.datetime.now().strftime('%m%d%H%M')}.txt", use_container_width=True)
    with c2:
        if st.button("🔄 清空全部", use_container_width=True):
            st.session_state.result_text = ""
            st.rerun()

    st.divider()
    st.subheader("💬 对话续稿区（续写/修改自动追加到结果末尾）")
    chat_input = st.chat_input("续写第二章、修改某段内容、优化台词...")
    if chat_input and api_key and st.session_state.result_text.strip():
        with st.spinner("正在处理..."):
            llm = ChatOpenAI(model="deepseek-chat", api_key=api_key.strip(), base_url=api_base, temperature=temperature)
            if "短剧" in mode or "剧本" in mode:
                prompt = f"""沿用原有剧本格式【场景｜镜头：人物台词】，基于原文：{st.session_state.result_text}，{chat_input}，不要改成小说"""
            else:
                prompt = f"""沿用网文风格，基于原文：{st.session_state.result_text}，{chat_input}"""
            resp = llm.invoke(prompt)
            new_txt = resp.content
            st.session_state.result_text += f"\n\n{new_txt}"
        st.rerun()
