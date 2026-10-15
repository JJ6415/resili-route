"""
Layer 5: Live Voice Dispatcher & 3D Commander Protocol
Generates verbal audio dispatches and 3D Avatar lip-sync commands purely with Google APIs (Google Gemini TTS & Cloud Text-to-Speech).
"""
from typing import Dict, Any, List, Optional
import base64
import json
import urllib.request
import logging
from pydantic import BaseModel, Field
from config import settings

logger = logging.getLogger("VoiceDispatcher")

class VoiceDispatchPayload(BaseModel):
    dispatch_type: str                  # "FINOPS_APPROVAL", "EARTHQUAKE_EVACUATION", "STRANDED_RESCUE", "MISSION_REPORT"
    speaker_name: str = "ResiliRoute 3D BCP Commander"
    spoken_text: str
    emotion: str = "calm"               # "calm", "urgent", "reassuring", "authoritative"
    subtitles: List[Dict[str, Any]] = []
    avatar_animation_state: str         # "SPEAKING_NORMAL", "ALERT_GESTURE", "EMERGENCY_DIRECTIVE"
    audio_base64: Optional[str] = None  # Google synthesized audio (base64)
    audio_mime_type: str = "audio/wav"
    tts_engine: str = "GOOGLE_GEMINI_TTS"

class VoiceDispatcher:
    """
    Dispatcher generating Japanese voice scripts, Google Gemini / Cloud TTS audio, and animation directives.
    """

    def synthesize_speech_gcp(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Synthesizes Japanese speech strictly using Google APIs:
        1. Primary: Google Gemini Dedicated TTS model (gemini-3.8-flash-tts / gemini-2.5-flash-preview-tts)
        2. Secondary: Google Cloud Text-to-Speech API
        Returns dict with audio_base64 and audio_mime_type, or None if network fails.
        """
        # 1. Primary: Google Gemini Native Audio TTS
        try:
            for tts_model in ["gemini-3.8-flash-tts", "gemini-2.5-flash-preview-tts"]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{tts_model}:generateContent?key={settings.GEMINI_API_KEY}"
                body = {"contents": [{"parts": [{"text": text}]}]}
                req = urllib.request.Request(
                    url,
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "inlineData" in parts[0]:
                            return {
                                "audio_base64": parts[0]["inlineData"]["data"],
                                "audio_mime_type": parts[0]["inlineData"].get("mimeType", "audio/wav"),
                                "engine": f"GOOGLE_{tts_model.upper().replace('-', '_')}"
                            }
        except Exception as e:
            logger.warning(f"Google Gemini Native TTS failed: {e}. Trying Google Cloud TTS...")

        # 2. Secondary: Google Cloud Text-to-Speech API
        try:
            import google.cloud.texttospeech as tts
            client = tts.TextToSpeechClient()
            s_input = tts.SynthesisInput(text=text)
            voice = tts.VoiceSelectionParams(
                language_code="ja-JP",
                name="ja-JP-Neural2-B",
                ssml_gender=tts.SsmlVoiceGender.FEMALE
            )
            audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)
            response = client.synthesize_speech(input=s_input, voice=voice, audio_config=audio_config)
            return {
                "audio_base64": base64.b64encode(response.audio_content).decode("utf-8"),
                "audio_mime_type": "audio/mp3",
                "engine": "GOOGLE_CLOUD_TEXT_TO_SPEECH"
            }
        except Exception as e:
            logger.warning(f"Google Cloud TTS Client failed: {e}")

        return None

    def dispatch_finops_approval(
        self,
        employee_name: str = "田中 主任",
        savings_jpy: int = 4470,
        approved_seat: str = "普通車指定席"
    ) -> VoiceDispatchPayload:
        text = (
            f"{employee_name}様、来週火曜日の東京発・新大阪行き「のぞみ」出張申請です。"
            f"旅費規程第14条に基づき、申請原案のグリーン車から{approved_seat}へ自動調整され、"
            f"{savings_jpy:,}円の経費削減を達成しました。電子決裁が正常に完了しました。"
        )
        res = self.synthesize_speech_gcp(text)
        return VoiceDispatchPayload(
            dispatch_type="FINOPS_APPROVAL",
            spoken_text=text,
            emotion="calm",
            subtitles=[{"text": text, "start_time": 0.0, "end_time": 5.5}],
            avatar_animation_state="SPEAKING_NORMAL",
            audio_base64=res["audio_base64"] if res else None,
            audio_mime_type=res["audio_mime_type"] if res else "audio/wav",
            tts_engine=res["engine"] if res else "GOOGLE_API_OFFLINE"
        )

    def dispatch_earthquake_evacuation(
        self,
        bottleneck_index: float = 0.92,
        total_employees: int = 120
    ) -> VoiceDispatchPayload:
        text = (
            f"緊急避難指令を発令します。首都圏で震度6強の地震が発生し、新宿駅の群衆事故ボトルネック指数が{bottleneck_index}に達しました。"
            f"新宿駅構内への進入を全面遮断します。社員{total_employees}名は、Slackに配信された3つの分散避難ルート、"
            f"明治神宮緑道および初台バスエリアへ直ちに迂回避難してください。"
        )
        res = self.synthesize_speech_gcp(text)
        return VoiceDispatchPayload(
            dispatch_type="EARTHQUAKE_EVACUATION",
            spoken_text=text,
            emotion="urgent",
            subtitles=[{"text": text, "start_time": 0.0, "end_time": 7.0}],
            avatar_animation_state="EMERGENCY_DIRECTIVE",
            audio_base64=res["audio_base64"] if res else None,
            audio_mime_type=res["audio_mime_type"] if res else "audio/wav",
            tts_engine=res["engine"] if res else "GOOGLE_API_OFFLINE"
        )

    def dispatch_stranded_rescue(
        self,
        employee_name: str = "佐藤 課長",
        shelter_name: str = "六本木ヒルズ 森タワー 3F防災センター"
    ) -> VoiceDispatchPayload:
        text = (
            f"{employee_name}様、緊急救援管制です。六本木一帯の鉄道が全面運休しました。"
            f"現在地から300メートルの特等級耐震提携避難所「{shelter_name}」へ直ちに移動してください。"
            f"画面のターンバイターン安全避難ルートと入館QR認証パスをご確認ください。"
        )
        res = self.synthesize_speech_gcp(text)
        return VoiceDispatchPayload(
            dispatch_type="STRANDED_RESCUE",
            spoken_text=text,
            emotion="reassuring",
            subtitles=[{"text": text, "start_time": 0.0, "end_time": 6.5}],
            avatar_animation_state="ALERT_GESTURE",
            audio_base64=res["audio_base64"] if res else None,
            audio_mime_type=res["audio_mime_type"] if res else "audio/wav",
            tts_engine=res["engine"] if res else "GOOGLE_API_OFFLINE"
        )

    def dispatch_mission_report(self) -> VoiceDispatchPayload:
        text = (
            "災害対策管制センターより報告します。本社社員120名および外出中の佐藤課長を含む全役職員の100%安全避難完了を確認しました。"
            "平時はスマートに旅費を経費削減し、有事にはわずか0.1秒で社員の命を守るResiliRouteのブリーフィングを終了します。"
        )
        res = self.synthesize_speech_gcp(text)
        return VoiceDispatchPayload(
            dispatch_type="MISSION_REPORT",
            spoken_text=text,
            emotion="authoritative",
            subtitles=[{"text": text, "start_time": 0.0, "end_time": 8.0}],
            avatar_animation_state="SPEAKING_NORMAL",
            audio_base64=res["audio_base64"] if res else None,
            audio_mime_type=res["audio_mime_type"] if res else "audio/wav",
            tts_engine=res["engine"] if res else "GOOGLE_API_OFFLINE"
        )
