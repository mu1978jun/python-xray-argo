#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import streamlit as st
import json
import base64
import uuid

st.set_page_config(page_title="ArgoSB一键生成", page_icon="🌐", layout="wide")

# 生成VMess链接
def generate_vmess_link(config):
    vmess_obj = {
        "v": "2",
        "ps": config.get("ps", "Argo节点"),
        "add": config.get("add", ""),
        "port": str(config.get("port", "443")),
        "id": config.get("id", ""),
        "aid": "0",
        "net": "ws",
        "type": "none",
        "host": config.get("host", ""),
        "path": config.get("path", ""),
        "tls": config.get("tls", ""),
        "sni": config.get("sni", "")
    }
    b64_str = base64.b64encode(json.dumps(vmess_obj).encode("utf-8")).decode("utf-8").rstrip("=")
    return f"vmess://{b64_str}"

# 批量生成优选IP节点
def make_all_nodes(domain, user_uuid):
    ws_path = f"/{user_uuid[:8]}-vm?ed=2048"
    node_list = []

    tls_ip = {
        "104.16.0.0":"443",
        "104.17.0.0":"8443",
        "104.18.0.0":"2053",
        "104.19.0.0":"2083",
        "104.20.0.0":"2087"
    }
    http_ip = {
        "104.21.0.0":"80",
        "104.22.0.0":"8080",
        "104.24.0.0":"8880"
    }

    # TLS节点
    for ip, p in tls_ip.items():
        node_list.append(generate_vmess_link({
            "ps": f"CF-TLS-{ip}",
            "add": ip, "port": p, "id": user_uuid,
            "host": domain, "path": ws_path, "tls": "tls", "sni": domain
        }))
    # HTTP节点
    for ip, p in http_ip.items():
        node_list.append(generate_vmess_link({
            "ps": f"CF-HTTP-{ip}",
            "add": ip, "port": p, "id": user_uuid,
            "host": domain, "path": ws_path, "tls": "", "sni": ""
        }))
    # 域名直连TLS
    node_list.append(generate_vmess_link({
        "ps": f"直连TLS-{domain}",
        "add": domain, "port": "443", "id": user_uuid,
        "host": domain, "path": ws_path, "tls": "tls", "sni": domain
    }))
    return node_list

# 页面UI
st.title("🌐 ArgoSB 节点生成器")
st.divider()

col1, col2 = st.columns(2)
with col1:
    input_domain = st.text_input("填写自定义域名", placeholder="streamlit.ccuu.de5.net")
    input_uuid = st.text_input("填写UUID", placeholder="d9893ccb-3227-4b3a-ab22-26bfbed89a9b")
with col2:
    input_token = st.text_input("填写Cloudflare Token", placeholder="eyJhIjoiOTQxMTg5MzAzZTAzN2ZlMmUxYjgwZWIyZjgwODM1ZGEiLCJ0IjoiMzAwNzc4OGMtYThiMy00NzYzLTgwYjItZWU0ZDk2NTdiYWQyIiwicyI6IllXVmlZMlZsT0RNdFptVm1PUzAwWlRSa0xXRTFPV010TjJNelptUmhPRGhrTURnMiJ9", type="password")
    auto_uuid = st.checkbox("空UUID自动随机生成", value=True)

st.divider()

if st.button("✨ 一键生成全部节点", type="primary", use_container_width=True):
    # 处理UUID
    if not input_uuid.strip() and auto_uuid:
        use_uuid = str(uuid.uuid4())
        st.info(f"自动生成UUID：{use_uuid}")
    else:
        use_uuid = input_uuid.strip()

    if not input_domain.strip():
        st.error("请填入隧道域名！")
        st.stop()
    if not use_uuid:
        st.error("请填入UUID或开启自动生成！")
        st.stop()

    nodes = make_all_nodes(input_domain.strip(), use_uuid)
    all_text = "\n".join(nodes)

    st.success("✅ 节点生成完成！")
    st.text_area("全部VMess节点链接", value=all_text, height=400)
    st.download_button("📥 下载TXT订阅", data=all_text, file_name="argo_node.txt")

st.divider()
st.caption("提示：Token仅用于记录留存，本页面不启动任何隧道进程，纯离线生成链接，Streamlit稳定不黑屏")
