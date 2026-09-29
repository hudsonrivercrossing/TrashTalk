# 咖啡馆对话录音转写

本项目使用 AssemblyAI 转写以中文为主、夹杂英文的双人对话，并保留说话人区分。原始录音放在 `audio/originals/`；不要改动原件。运行前检查 `ASSEMBLYAI_API_KEY` 是否已保存在本地 `.env.local`，不要把 key 发到聊天或写进项目文件。

## 转写

在项目根目录运行本机预检（不会上传音频）：

```sh
python transcribe_assemblyai.py --check 'audio/originals/录音文件.m4a'
```

提交转写会上传音频到 AssemblyAI，并可能产生费用：

```sh
python transcribe_assemblyai.py 'audio/originals/录音文件.m4a'
```

脚本会为每个音频建立独立目录：`transcripts/assemblyai/<录音文件名>/`，里面保存 AssemblyAI 结构化结果 `.assemblyai.diarized.json` 和便于阅读的 `.assemblyai.diarized.txt`。如果文件已经存在，脚本会拒绝覆盖。

## 发布稿

将润色后的 longform Markdown 也放在对应录音目录，例如：

```text
transcripts/assemblyai/录音文件名/录音文件名.publish-longform.md
```

保留原始 API 结果和中间稿；不要覆盖用户已经编辑过的发布稿。说话人默认保留 A/B 标签，不根据 `spk_1`、`spk_2` 猜测真实身份。
