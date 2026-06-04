import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import datetime
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

# ==========页面配置必须放最顶部==========
st.set_page_config(page_title="网文+短剧AI生成器", layout="wide", page_icon="📝")

# ==========CSS：删除侧边空白、压缩多余边距==========
css = """
<style>
/*全局容器去空白*/
.block-container { padding:0.6rem 1rem !important; max-width:100% !important; }
/*侧边栏去除上下大块空白*/
section[data-testid="stSidebar"] { padding-top:0px !important; }
section[data-testid="stSidebar"] > div:first-child { padding-top:0.2rem !important; padding-bottom:0 !important; }
/*卡片底色不变，压缩内边距*/
[data-testid="stColumn"]:first-child > div > div {background:#b4cfc2;border-radius:14px;padding:12px 15px;box-shadow:0 2px 5px rgba(180,207,194,0.3);}
[data-testid="stColumn"]:nth-child(2) > div:nth-child(1) > div {background:#92b8a7;border-radius:14px;padding:12px 15px;box-shadow:0 2px 5px rgba(146,184,167,0.3);}
[data-testid="stColumn"]:nth-child(2) > div:nth-child(2) > div {background:#7398d8;border-radius:14px;padding:12px 15px;box-shadow:0 2px 5px rgba(115,152,216,0.3);}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stSelectbox>div{background:#d1e4dd;border:1px solid #b4cfc2;}
.stButton>button{background:#5a8272;color:#fff;border:none;border-radius:9px;}
.stButton>button:hover{background:#4a7162;}
h1,h2,h3{color:#3a504a; margin-top:0.3rem; margin-bottom:0.5rem;}
.stChatMessage{background:#d1e4dd;border-radius:10px;}
#MainMenu,footer,header{display:none;}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ==========状态初始化==========
if "messages" not in st.session_state:
    st.session_state.messages = []
# 主结果文本，核心绑定项
if "result_text" not in st.session_state:
    st.session_state.result_text = ""

st.markdown("<h1 style='text-align:center;margin:5px 0;'>📝 网文 + 短剧剧本 双模式 AI 生成器</h1>",unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#3a504a;margin-bottom:8px;'>支持：大纲生成 | 章节写作 | 短剧剧本 | 拆书仿写 | 对话续稿</p>",unsafe_allow_html=True)
st.divider()

left_bar, right_area = st.columns([0.35, 0.65])

# ==========左侧配置区（无多余空白）==========
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
    # 全新生成按钮：内容直接进主结果+历史
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
                # 核心：直接赋值主结果，页面立刻刷新展示
                st.session_state.result_text = content
                st.session_state.messages.append(HumanMessage(content=f"新建生成：{mode} {user_input}"))
                st.session_state.messages.append(AIMessage(content=content))
                st.success("初次生成完成，内容已展示在右侧结果框")

# ==========右侧结果区（修复：生成内容固定显示此处）==========
with right_area:
    st.subheader("📄 生成结果")
    # 关键：value绑定session_state.result_text，实时同步，云端打开只要有数据就显示
    st.text_area("最终内容", value=st.session_state.result_text, height=300, key="result_box")

    c1,c2 = st.columns(2)
    with c1:
        if st.session_state.result_text.strip():
            st.download_button("💾 下载 TXT", st.session_state.result_text,
                               file_name=f"AI创作_{datetime.datetime.now().strftime('%m%d%H%M')}.txt", use_container_width=True)
    with c2:
        if st.button("🔄 清空全部", use_container_width=True):
            st.session_state.result_text = ""
            st.session_state.messages = []
            st.rerun()

    st.divider()
    st.subheader("💬 对话续稿区（续写/修改自动追加到结果末尾）")
    chat_input = st.chat_input("续写第二章、修改某段内容、优化台词...")
    if chat_input and api_key and st.session_state.result_text.strip():
        st.session_state.messages.append(HumanMessage(content=f"修改/续写指令：{chat_input}"))
        with st.chat_message("user",avatar="👤"):
            st.markdown(chat_input)
        with st.chat_message("assistant",avatar="🤖"):
            with st.spinner("正在处理..."):
                llm = ChatOpenAI(model="deepseek-chat", api_key=api_key.strip(), base_url=api_base, temperature=temperature)
                if "短剧" in mode or "剧本" in mode:
                    prompt = f"""沿用原有剧本格式【场景｜镜头：人物台词】，基于原文：{st.session_state.result_text}，{chat_input}，不要改成小说"""
                else:
                    prompt = f"""沿用网文风格，基于原文：{st.session_state.result_text}，{chat_input}"""
                resp = llm.invoke(prompt)
                new_txt = resp.content
                st.markdown(new_txt)
                st.session_state.messages.append(AIMessage(content=new_txt))
                # 续写追加到主结果末尾
                st.session_state.result_text += f"\n\n{new_txt}"
                st.rerun() # 强制刷新结果框，立刻显示新增内容

    st.divider()
    st.subheader("📜 创作历史记录（仅备份，点回填才替换结果）")
    chat_container = st.container(height=200)
    with chat_container:
        for idx, msg in enumerate(st.session_state.messages):
            if isinstance(msg, HumanMessage):
                st.chat_message("user", avatar="📝").write(msg.content)
            else:
                col_msg, col_btn = st.columns([0.82,0.18])
                with col_msg:
                    st.chat_message("assistant", avatar="🤖").write(msg.content)
                with col_btn:
                    if st.button(f"回填{idx}",key=f"fill_{idx}"):
                        st.session_state.result_text = msg.content
                        st.rerun()
