import datetime
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

st.set_page_config(page_title="青笺 · AI 创作工坊", page_icon="✦", layout="wide")

def clear_draft():
    """Clear the editor before Streamlit instantiates its text area widget."""
    st.session_state.draft = ""
    st.session_state.draft_editor = ""

PALETTE_CSS = """
<style>
:root { --ink:#29483f; --muted:#527267; --mint:#d1e4dd; --sage:#b4cfc2;
--mist:#92b8a7; --pine:#739f8d; --deep:#416f60; --paper:#f5faf7; --line:#dceae3; }
.stApp { background:linear-gradient(145deg,#f8fbf9 0%,#edf6f1 58%,#e5f0ea 100%); color:var(--ink); }
[data-testid="stHeader"] { background:rgba(245,250,247,.82); }
.block-container { max-width:1440px; padding-top:2rem; padding-bottom:3rem; }
h1,h2,h3,p,label,span,div { color:inherit; }
h1,h2,h3 { color:var(--ink)!important; }
[data-testid="stSidebar"] { background:#e5f0ea; }
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stNumberInput"] input { background:#fff!important; color:#243c34!important;
border:1px solid #b4cfc2!important; border-radius:10px!important; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div { background:#fff!important; color:#243c34!important; }
[data-testid="stSelectbox"] [data-baseweb="select"] input { color:#243c34!important; }
[data-baseweb="popover"] ul,[data-baseweb="menu"] { background:#fff!important; }
[data-baseweb="popover"] li,[data-baseweb="menu"] li { color:#243c34!important; }
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder { color:#71877e!important; }
[data-testid="stTextArea"] textarea { line-height:1.65; }
.stButton button,.stDownloadButton button { background:#5a8272!important; color:white!important;
border:0!important; border-radius:10px!important; transition:transform .18s ease,box-shadow .18s ease,background .18s ease; }
.stButton button:hover,.stDownloadButton button:hover { background:#416f60!important; transform:translateY(-2px); box-shadow:0 7px 18px #416f6030; }
[data-testid="stMetric"] { background:#ffffffb8; border:1px solid var(--line); padding:14px; border-radius:14px; }
[data-testid="stVerticalBlockBorderWrapper"] { background:#ffffffb8; border-color:var(--line)!important; border-radius:18px; }
[data-testid="stMarkdownContainer"] { color:var(--ink); }
section[data-testid="stSidebar"] { border-right:1px solid var(--line); }
@keyframes rise { from {opacity:0;transform:translateY(10px)} to {opacity:1;transform:translateY(0)} }
.hero { text-align:center; padding:1.6rem 1rem 1.2rem; animation:rise .65s ease both; }
.hero h1 { font-size:2.55rem; letter-spacing:.05em; margin-bottom:.25rem; }
.hero p { color:var(--muted); font-size:1.05rem; }
.step-card { background:#ffffffb8; border:1px solid var(--line); border-radius:18px; padding:1rem 1.2rem; animation:rise .45s ease both; }
.stProgress > div > div > div > div { background:#739f8d; }
@media (prefers-reduced-motion: reduce) { *,*::before,*::after { animation:none!important; transition:none!important; } }
</style>
"""
st.markdown(PALETTE_CSS, unsafe_allow_html=True)


def get_secret(name: str, default: str = "") -> str:
    """Read a secret from Streamlit Cloud secrets first, then local environment."""
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = default
    return str(value or os.getenv(name, default)).strip()


def build_prompt(mode: str, theme: str, protagonist: str, setting: str,
                 keywords: str, request: str, length: str) -> str:
    context = (f"作品题材：{theme}\n主角设定：{protagonist or '请根据题材设计'}\n"
               f"世界/背景：{setting or '由创作需要补充'}\n核心元素：{keywords or '无特别要求'}\n"
               f"目标篇幅：{length}\n创作要求：{request}")
    if mode == "故事大纲":
        task = "请输出一句话故事核心、主要人物关系、故事规则、分卷/分集大纲、核心冲突和结尾走向。层次清楚，避免空泛套路。"
    elif mode == "网文章节":
        task = "创作一章可直接阅读的网文正文。先承接设定，开头尽快进入冲突，人物行动符合动机，结尾留下自然的阅读钩子。不要输出创作说明。"
    else:
        task = "创作可拍摄的短剧剧本，按场次编号，写明场景、时间、人物、动作和对白；每场推动冲突，结尾设置明确反转或悬念。不要写小说式心理描写。"
    return f"你是一名专业的网文与短剧编剧。请遵守用户设定，不擅自改变人物关系。\n\n{context}\n\n任务：{task}"


def call_model(prompt: str, temperature: float) -> str:
    key = get_secret("DEEPSEEK_API_KEY")
    if not key:
        raise ValueError("未找到 API 密钥。请在本地 .env 或 Streamlit Cloud Secrets 中配置 DEEPSEEK_API_KEY。")
    base_url = get_secret("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    model_name = get_secret("DEEPSEEK_MODEL", "deepseek-chat")
    llm = ChatOpenAI(model=model_name, api_key=key, base_url=base_url,
                     temperature=temperature, timeout=60, max_retries=1)
    response = llm.invoke(prompt)
    if not isinstance(response.content, str) or not response.content.strip():
        raise ValueError("模型返回了空内容，请调整要求后重试。")
    return response.content.strip()


if "draft" not in st.session_state:
    st.session_state.draft = ""
if "draft_editor" not in st.session_state:
    st.session_state.draft_editor = ""
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

st.markdown("""
<div class="hero"><h1>✦ 故事造梦间</h1>
<p>把灵感写成大纲、章节与短剧</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("创作控制台")
    mode = st.selectbox("创作任务", ["故事大纲", "网文章节", "短剧剧本"])
    theme = st.text_input("题材", placeholder="例如：都市悬疑、重生成长")
    protagonist = st.text_area("主角设定", height=90, placeholder="身份、目标、性格、弱点")
    setting = st.text_area("世界与背景", height=90, placeholder="时代、地点、故事规则")
    keywords = st.text_input("关键词 / 情绪爽点", placeholder="反转、成长、复仇……")
    request = st.text_area("本次具体要求", height=130, placeholder="写清楚这一轮要产出什么、避免什么")
    length = st.select_slider("篇幅", options=["短", "中", "长"], value="中")
    temperature = st.slider("创意程度", 0.1, 1.2, 0.7, 0.1)
    generate = st.button("✦ 生成初稿", type="primary", use_container_width=True)
    st.caption("密钥由本地 .env 或部署 Secrets 提供，网页不接收也不展示密钥。")

st.subheader("创作工作台")
st.markdown('<div class="step-card">① 补全故事设定　→　② 生成初稿　→　③ 在下方直接编辑与续写</div>', unsafe_allow_html=True)
if generate:
    if not theme.strip():
        st.error("先填写题材，帮助模型确定创作方向。")
    elif not request.strip():
        st.error("请填写本次具体要求。")
    elif len(request) > 8000 or len(protagonist) > 3000 or len(setting) > 3000:
        st.error("单项输入过长，请精简后再生成。")
    else:
        st.session_state.last_prompt = build_prompt(mode, theme.strip(), protagonist.strip(), setting.strip(), keywords.strip(), request.strip(), length)
        try:
            with st.status("正在整理设定并创作…", expanded=True) as status:
                st.write("准备创作指令")
                st.progress(35)
                draft = call_model(st.session_state.last_prompt, temperature)
                st.progress(100)
                st.session_state.draft = draft
                st.session_state.draft_editor = draft
                status.update(label="初稿已完成", state="complete", expanded=False)
        except Exception as exc:
            st.error(str(exc) if isinstance(exc, ValueError) else "请求失败，请检查网络、密钥配置和 API 地址后重试。")
            st.caption(f"错误类型：{type(exc).__name__}；已有草稿不会被清除。")

st.markdown("#### 可编辑初稿")
st.text_area("生成内容（可直接修改）", height=430, label_visibility="collapsed", key="draft_editor")
st.session_state.draft = st.session_state.draft_editor

a, b, c = st.columns(3)
with a:
    if st.button("继续写 / 修改", use_container_width=True, disabled=not st.session_state.draft.strip()):
        if not request.strip():
            st.warning("请在左侧填写本次续写或修改要求。")
        elif len(st.session_state.draft) > 16000:
            st.warning("草稿太长，暂时无法整体带入修改；请先缩短草稿。")
        else:
            followup = f"沿用既有人物、设定和文风，完成用户要求。不要重复已有内容。\n\n已有草稿：\n{st.session_state.draft}\n\n本次要求：\n{request}"
            try:
                with st.spinner("正在续写或修改…"):
                    addition = call_model(followup, temperature)
                st.session_state.draft += "\n\n" + addition
                st.session_state.draft_editor = st.session_state.draft
                st.rerun()
            except Exception as exc:
                st.error(str(exc) if isinstance(exc, ValueError) else "续写失败，请检查网络和 API 配置。")
with b:
    st.download_button("下载 Markdown", data=st.session_state.draft,
                       file_name=f"青笺创作_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
                       mime="text/markdown", use_container_width=True, disabled=not st.session_state.draft.strip())
with c:
    st.button("清空草稿", use_container_width=True, on_click=clear_draft)

st.caption("草稿只保留在当前会话中；下载 Markdown 可保存创作结果。")
