# Airi_python
uvicorn api:api --host 0.0.0.0 --port 8000
<img width="1788" height="855" alt="image" src="https://github.com/user-attachments/assets/9f748a6d-ee0e-4aa8-a2c9-c4289053f8c3" />
项目本身是https://mp.weixin.qq.com/s/kb5GlMu_vTrvq2YoyfcP-g  《Airi：开箱即用的 AI 端侧语音助理框架》
因为会python，就用chatgpt给理了一下框架，又让它复刻了 python 版本，这样下载玩代码还是不能跑的，给到cursor，直接几分钟搞定，cursor现在好快好厉害。
于是我又用手头的局域网显卡和一台云电脑，把网站部署了出去。
《一台局域网服务器、一台云电脑、一个域名，通过frp，可以碰撞怎么样的火花——一个陪伴机器人的诞生》
面对一个棘手的问题：局域网服务器无法暴露外部端口，所以无法用到这个服务器内强大的显卡，对外部提供服务。
但是有一台性能低的云服务器和一个域名。
所以使用反代理工具frp，所有局域网服务器的数据，都可以通过反代理工具frp，发送到云服务器，云电脑上还绑定了域名，这样他竟然利用局域网的算力部署的网站，外界可以通过域名访问了。




