/**
 * ResiliRoute Main Frontend Orchestration
 * Localized in Japanese.
 * Handles:
 * - Real-time Status & Telemetry Polling
 * - Three.js WebGL 3D Avatar (with Google Cloud TTS Japanese Audio)
 * - Leaflet GIS Real-time Map (Tokyo Metro GIS)
 * - Tri-Line Canvas Trajectory Chart
 * - Web Speech Recognition (STT, ja-JP) & Prominent Top-Left Command Bar
 * - Simulation Scenario Triggers (Non-mock Engine Pipeline)
 */
document.addEventListener('DOMContentLoaded', () => {
  let chart = null;
  let avatar = null;
  let gisMap = null;

  // Initialize Canvas Chart
  if (window.TrajectoryChart) {
    chart = new window.TrajectoryChart('trajectoryCanvas');
  }

  // Initialize Three.js 3D Commander Avatar
  if (window.CommanderAvatar) {
    avatar = new window.CommanderAvatar('avatarBox');
  }

  // Initialize Leaflet GIS Interactive Map
  if (window.GisMap) {
    gisMap = new window.GisMap('gisMapContainer');
  }

  // UI elements
  const body = document.body;
  const statusPill = document.getElementById('statusPill');
  const statusPillText = document.getElementById('statusPillText');
  const bottleneckVal = document.getElementById('bottleneckVal');
  const bottleneckStatus = document.getElementById('bottleneckStatus');
  const cacheBackendText = document.getElementById('cacheBackendText');
  const logContainer = document.getElementById('logInspector');
  const dispatchBox = document.getElementById('dispatchPreviewBox');

  // View Switcher (GIS Map vs Tri-Line Trajectory)
  window.switchMainView = (viewName) => {
    const tabMapBtn = document.getElementById('tabMapBtn');
    const tabTrajectoryBtn = document.getElementById('tabTrajectoryBtn');
    const gisMapView = document.getElementById('gisMapView');
    const trajectoryView = document.getElementById('trajectoryView');

    if (viewName === 'map') {
      if (tabMapBtn) tabMapBtn.classList.add('active');
      if (tabTrajectoryBtn) tabTrajectoryBtn.classList.remove('active');
      if (gisMapView) gisMapView.style.display = 'block';
      if (trajectoryView) trajectoryView.style.display = 'none';
      if (gisMap) gisMap.invalidateSize();
    } else {
      if (tabMapBtn) tabMapBtn.classList.remove('active');
      if (tabTrajectoryBtn) tabTrajectoryBtn.classList.add('active');
      if (gisMapView) gisMapView.style.display = 'none';
      if (trajectoryView) trajectoryView.style.display = 'block';
      if (chart) chart.render();
    }
  };

  // Quick prompt chip fill & immediate orchestration execution
  window.fillPrompt = (text) => {
    const input = document.getElementById('userChatInput');
    if (input) {
      input.value = text;
      input.focus();
    }
    if (typeof handleUserChat === 'function') {
      handleUserChat(text);
    }
  };

  // Load Initial Status & Trajectory
  async function refreshStatus() {
    try {
      const res = await fetch('/v1/mobility/status');
      const data = await res.json();

      // Theme toggle
      if (data.is_bcp_mode) {
        body.classList.add('bcp-active');
        statusPill.className = 'status-pill emergency';
        statusPillText.textContent = 'BCP EMERGENCY ACTIVE (0.1秒 切替完了)';
        if (avatar) avatar.setAlert(true);
      } else {
        body.classList.remove('bcp-active');
        statusPill.className = 'status-pill';
        statusPillText.textContent = 'NORMAL FINOPS ACTIVE (平時旅費ガバナンス)';
        if (avatar) avatar.setAlert(false);
      }

      // Bottleneck Index
      const bIdx = data.shinjuku_bottleneck_index || 0.15;
      bottleneckVal.textContent = bIdx.toFixed(2);
      if (bIdx >= 0.70) {
        bottleneckVal.style.color = '#ef4444';
        bottleneckStatus.textContent = '危険限界超過 (新宿駅構内進入即時遮断)';
      } else {
        bottleneckVal.style.color = '#10b981';
        bottleneckStatus.textContent = '安全収容範囲内 (正常通行)';
      }

      // Cache telemetry
      if (data.cache_stats) {
        cacheBackendText.textContent = `${data.cache_stats.backend} (${data.cache_stats.status})`;
      }

      // Render Logs
      if (data.recent_logs && data.recent_logs.length > 0) {
        renderLogs(data.recent_logs);
      }
    } catch (e) {
      console.warn('Status refresh error:', e);
    }
  }

  async function loadTrajectory() {
    try {
      const res = await fetch('/v1/mobility/trajectory');
      const data = await res.json();
      if (chart) chart.updateData(data);
      updateChartLegend(data);
    } catch (e) {
      console.warn('Trajectory fetch error:', e);
    }
  }

  function updateChartLegend(data) {
    const l1Name = document.getElementById('legendL1Name');
    const l2Name = document.getElementById('legendL2Name');
    const l3Name = document.getElementById('legendL3Name');
    const shadeName = document.getElementById('legendShadeName');
    const summaryMetric = document.getElementById('trajectorySummaryMetric');

    if (l1Name) l1Name.textContent = data.line1_name;
    if (l2Name) l2Name.textContent = data.line2_name;
    if (l3Name) l3Name.textContent = data.line3_name;
    if (shadeName) shadeName.textContent = data.shading_area_label;
    if (summaryMetric) summaryMetric.textContent = data.summary_metric;
  }

  function renderLogs(logs) {
    if (!logContainer) return;
    logContainer.innerHTML = '';
    logs.forEach(l => {
      const row = document.createElement('div');
      row.className = 'log-line';
      const tagClass = `tag-${(l.tag || 'system').toLowerCase()}`;
      row.innerHTML = `
        <span class="log-time">[${l.timestamp}]</span>
        <span class="log-tag ${tagClass}">${l.tag || 'LOG'}</span>
        <span class="log-msg">${l.message}</span>
      `;
      logContainer.appendChild(row);
    });
  }

  // Simulation Deck Triggers
  window.triggerScenario = async (scenarioId) => {
    try {
      const btn = document.querySelector(`.sim-btn[data-scenario="${scenarioId}"]`);
      if (btn) btn.classList.add('active');

      const res = await fetch('/v1/simulation/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: scenarioId })
      });
      const data = await res.json();

      setTimeout(() => {
        if (btn) btn.classList.remove('active');
      }, 600);

      // Update GIS Map corresponding to scenario
      if (gisMap) {
        if (scenarioId === 1) {
          gisMap.renderNormalShinkansen();
        } else if (scenarioId === 2) {
          const bIdx = (data.output_summary && data.output_summary.shinjuku_bottleneck_index) || 0.92;
          gisMap.renderDisasterShinjuku(bIdx);
        } else if (scenarioId === 3) {
          gisMap.renderStrandedRoppongi();
        }
      }

      // Update Trajectory Chart
      if (data.visualizer_data && chart) {
        chart.updateData(data.visualizer_data);
        updateChartLegend(data.visualizer_data);
      }

      // Voice Dispatch & Speech strictly via Google Cloud / Gemini TTS
      if (data.voice_dispatch && avatar) {
        avatar.speak(
          data.voice_dispatch.spoken_text,
          data.voice_dispatch.audio_base64,
          data.voice_dispatch.audio_mime_type
        );
      }

      // Render Preview Card
      renderScenarioCard(scenarioId, data.output_summary);
      refreshStatus();
    } catch (e) {
      alert('シミュレーション実行エラー: ' + e);
    }
  };

  window.resetSystem = async () => {
    try {
      await fetch('/v1/mobility/reset', { method: 'POST' });
      await refreshStatus();
      await loadTrajectory();
      if (gisMap) {
        gisMap.renderNormalShinkansen();
      }
      if (avatar) {
        avatar.speak('システムが正常な平時ガバナンスモードにリセットされました。');
      }
      if (dispatchBox) {
        dispatchBox.innerHTML = '<p style="color:#64748b; font-size:0.85rem;">上部のシミュレーションボタンを押すか、対話入力欄に出張または救護メッセージを入力してください。</p>';
      }
    } catch (e) {
      alert('リセット失敗: ' + e);
    }
  };

  function renderScenarioCard(scenarioId, summary) {
    if (!dispatchBox) return;

    if (scenarioId === 1) {
      dispatchBox.innerHTML = `
        <div style="border-left: 3px solid var(--emerald); padding-left: 0.75rem;">
          <h4 style="color: var(--emerald); font-size: 0.95rem; margin-bottom: 0.4rem;">💚 【FinOps自律決裁完了】 ${summary.applicant}</h4>
          <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.3rem;">• 区間: <b>${summary.route}</b></p>
          <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.3rem;">• 規程調整: <s>${summary.original_request}</s> ──▶ <b>${summary.approved_selection}</b></p>
          <p style="font-size: 0.85rem; color: #6ee7b7; font-weight: 700;">• 削減成果: ${summary.cost_savings_jpy.toLocaleString()}円 削減 (${summary.savings_pct})</p>
          <div style="margin-top: 0.6rem; padding: 0.5rem; background: rgba(0,0,0,0.3); border-radius: 6px; font-size: 0.75rem; color: #94a3b8; font-family: var(--font-mono); white-space: pre-line;">
            ${summary.slack_notification}
          </div>
        </div>
      `;
    } else if (scenarioId === 2) {
      dispatchBox.innerHTML = `
        <div style="border-left: 3px solid var(--red-alert); padding-left: 0.75rem;">
          <h4 style="color: #fca5a5; font-size: 0.95rem; margin-bottom: 0.4rem;">🚨 【首都圏 震度6強 BCP】 社員 ${summary.total_evacuees}名 3グループ群衆分散</h4>
          <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• 新宿駅ボトルネック指数: <b style="color:#ef4444">${summary.shinjuku_bottleneck_index} (駅構内シャットダウン)</b></p>
          <p style="font-size: 0.8rem; color: #93c5fd; margin-bottom: 0.2rem;">• <b>グループA (40名)</b>: ${summary.group_a}</p>
          <p style="font-size: 0.8rem; color: #a7f3d0; margin-bottom: 0.2rem;">• <b>グループB (40名)</b>: ${summary.group_b}</p>
          <p style="font-size: 0.8rem; color: #fde047; margin-bottom: 0.4rem;">• <b>グループC (40名)</b>: ${summary.group_c}</p>
          <div style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 6px; font-size: 0.75rem;">
            <span style="color:#38bdf8; font-weight:600;">1:1 モバイル避難チケット配信サンプル:</span>
            <div style="margin-top: 0.3rem; color: #e2e8f0; font-family: var(--font-mono);">
              チケット: ${summary.tickets_sample[0].ticket_id} | 宛先: ${summary.tickets_sample[0].employee_name} (${summary.tickets_sample[0].department})
              <br>案内: ${summary.tickets_sample[0].route_guide}
            </div>
          </div>
        </div>
      `;
    } else if (scenarioId === 3) {
      dispatchBox.innerHTML = `
        <div style="border-left: 3px solid var(--purple); padding-left: 0.75rem;">
          <h4 style="color: #d8b4fe; font-size: 0.95rem; margin-bottom: 0.4rem;">🛡️ 【外勤帰宅困難者 提携避難所救援】 ${summary.stranded_employee}</h4>
          <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• 現在地: <b>${summary.location}</b></p>
          <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• マッチング避難所: <b>${summary.matched_bcp_shelter}</b> (${summary.distance})</p>
          <div style="margin-top: 0.5rem; font-size: 0.75rem; color: #cbd5e1;">
            <b>【ターンバイターン安全避難ルート】</b>
            <ol style="margin-left: 1.2rem; margin-top: 0.3rem; line-height: 1.4;">
              ${summary.turn_by_turn_guidance.map(step => `<li>${step}</li>`).join('')}
            </ol>
          </div>
          <div class="qr-preview-wrapper">
            <div class="qr-box">
              <div class="qr-placeholder"></div>
            </div>
            <div>
              <p style="font-size: 0.75rem; font-weight: 700; color: #38bdf8;">モバイルBCP入館認証パス</p>
              <p style="font-size: 0.7rem; color: #94a3b8; font-family: var(--font-mono);">${summary.qr_access_ticket}</p>
              <p style="font-size: 0.7rem; color: #4ade80;">安全確認完了: ${summary.safety_status}</p>
            </div>
          </div>
        </div>
      `;
    }
  }

  // Interactive Natural Language Message Box
  const userChatInput = document.getElementById('userChatInput');
  const userChatBtn = document.getElementById('userChatBtn');
  const micBtn = document.getElementById('micBtn');
  const voiceStatusBanner = document.getElementById('voiceStatusBanner');
  const voiceStatusText = document.getElementById('voiceStatusText');

  async function handleUserChat(textParam = null) {
    const text = (textParam || userChatInput.value || '').trim();
    if (!text) return;
    if (userChatInput) userChatInput.value = text;

    if (dispatchBox) {
      dispatchBox.innerHTML = `
        <div style="padding: 0.8rem; text-align: center; color: #38bdf8;">
          <span class="pulse-dot" style="display:inline-block; margin-right: 0.5rem;"></span>
          <b>【解析中】</b> AIモビリティ管制センターで発話を解析中... (DLP検証 & 最適経路選定)
        </div>
      `;
    }

    try {
      const res = await fetch('/v1/mobility/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, employee_name: '田中 主任', employee_rank: '主任' })
      });
      const data = await res.json();

      // Update trajectory
      if (data.trajectory && chart) {
        chart.updateData(data.trajectory);
        updateChartLegend(data.trajectory);
      }

      // Case 1: Stranded Rescue
      if (data.intent_type === 'STRANDED_RESCUE' || data.rescue_plan) {
        const rp = data.rescue_plan;
        if (gisMap) gisMap.renderStrandedRoppongi();
        if (data.voice_dispatch && avatar) {
          avatar.speak(
            data.voice_dispatch.spoken_text,
            data.voice_dispatch.audio_base64,
            data.voice_dispatch.audio_mime_type
          );
        }
        if (dispatchBox) {
          dispatchBox.innerHTML = `
            <div style="border-left: 3px solid var(--purple); padding-left: 0.75rem;">
              <h4 style="color: #d8b4fe; font-size: 0.95rem; margin-bottom: 0.4rem;">🛡️ 【外勤帰宅困難者 提携避難所救援】 ${rp.employee_name}</h4>
              <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• 原文Ingress DLP: <b>${data.sanitized_input}</b></p>
              <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• 現在地: <b>${rp.initial_location}</b></p>
              <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• マッチング避難所: <b>${rp.matched_shelter_name}</b> (${rp.distance_meters}m)</p>
              <div style="margin-top: 0.5rem; font-size: 0.75rem; color: #cbd5e1;">
                <b>【ターンバイターン安全避難ルート】</b>
                <ol style="margin-left: 1.2rem; margin-top: 0.3rem; line-height: 1.4;">
                  ${rp.turn_by_turn_route.map(step => `<li>${step}</li>`).join('')}
                </ol>
              </div>
              <div class="qr-preview-wrapper" style="margin-top:0.6rem;">
                <div class="qr-box">
                  <div class="qr-placeholder"></div>
                </div>
                <div>
                  <p style="font-size: 0.75rem; font-weight: 700; color: #38bdf8;">モバイルBCP入館認証パス</p>
                  <p style="font-size: 0.7rem; color: #94a3b8; font-family: var(--font-mono);">${rp.qr_access_pass_token}</p>
                  <p style="font-size: 0.7rem; color: #4ade80;">安全確認ステータス: ${rp.safety_confirmation_status}</p>
                </div>
              </div>
            </div>
          `;
        }
        refreshStatus();
        return;
      }

      // Case 2: Disaster Evacuation
      if (data.intent_type === 'DISASTER_EVACUATION' || data.crowd_balancing_plan) {
        const cp = data.crowd_balancing_plan;
        const bIdx = (data.bottleneck && data.bottleneck.bottleneck_index) || 0.92;
        if (gisMap) gisMap.renderDisasterShinjuku(bIdx);
        if (data.voice_dispatch && avatar) {
          avatar.speak(
            data.voice_dispatch.spoken_text,
            data.voice_dispatch.audio_base64,
            data.voice_dispatch.audio_mime_type
          );
        }
        if (dispatchBox) {
          dispatchBox.innerHTML = `
            <div style="border-left: 3px solid var(--red-alert); padding-left: 0.75rem;">
              <h4 style="color: #fca5a5; font-size: 0.95rem; margin-bottom: 0.4rem;">🚨 【首都圏 震度6強 BCP】 社員 120名 3グループ群衆分散</h4>
              <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• 原文Ingress DLP: <b>${data.sanitized_input}</b></p>
              <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• 新宿駅ボトルネック指数: <b style="color:#ef4444">${bIdx} (駅構内シャットダウン)</b></p>
              <p style="font-size: 0.8rem; color: #93c5fd; margin-bottom: 0.2rem;">• <b>グループA (40名)</b>: ${cp.group_a_shinjuku_gyoen.route_guide}</p>
              <p style="font-size: 0.8rem; color: #a7f3d0; margin-bottom: 0.2rem;">• <b>グループB (40名)</b>: ${cp.group_b_meiji_jingu.route_guide}</p>
              <p style="font-size: 0.8rem; color: #fde047; margin-bottom: 0.4rem;">• <b>グループC (40名)</b>: ${cp.group_c_hatsudai_buses.route_guide}</p>
              <div style="background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 6px; font-size: 0.75rem; margin-top:0.4rem;">
                <span style="color:#38bdf8; font-weight:600;">発行チケット数: ${data.total_tickets_issued || 120}件 (Slack / SMS即時配信完了)</span>
              </div>
            </div>
          `;
        }
        refreshStatus();
        return;
      }

      // Case 3: Normal FinOps Travel Booking
      if (gisMap) gisMap.renderNormalShinkansen();
      if (data.voice_dispatch && avatar) {
        avatar.speak(
          data.voice_dispatch.spoken_text,
          data.voice_dispatch.audio_base64,
          data.voice_dispatch.audio_mime_type
        );
      }
      const compliance = data.policy_compliance || {};
      const approval = data.approval_draft || {};
      const ekispertCourse = data.ekispert_course || {};
      if (dispatchBox) {
        dispatchBox.innerHTML = `
          <div style="border-left: 3px solid var(--emerald); padding-left: 0.75rem;">
            <h4 style="color: var(--emerald); font-size: 0.95rem; margin-bottom: 0.4rem;">💚 【FinOps自律決裁完了】 ${approval.applicant || '田中 主任'}</h4>
            <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• 原文Ingress DLP: <b>${data.sanitized_input}</b> (保護マスキング: ${data.masked_count || 0}件)</p>
            <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• 区間: <b>${approval.trip_route || '東京〜新大阪'}</b> (${ekispertCourse.train_name || 'のぞみ'})</p>
            <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.2rem;">• 規程調整: <s>グリーン車</s> ──▶ <b>${compliance.recommended_seat_type || '普通車指定席'}</b></p>
            <p style="font-size: 0.85rem; color: #6ee7b7; font-weight: 700;">• 削減成果: ${(compliance.cost_saving_jpy || 4470).toLocaleString()}円 削減 (${compliance.saving_percentage_label || '23.6%'})</p>
            <div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(0,0,0,0.3); border-radius: 6px; font-size: 0.75rem; color: #94a3b8; font-family: var(--font-mono); white-space: pre-line;">
              ${approval.slack_notification_preview || approval.justification || ''}
            </div>
          </div>
        `;
      }
      refreshStatus();
    } catch (e) {
      alert('リクエスト処理エラー: ' + e);
    }
  }

  window.handleUserChat = handleUserChat;

  if (userChatBtn) {
    userChatBtn.addEventListener('click', () => handleUserChat());
  }
  if (userChatInput) {
    userChatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleUserChat();
    });
  }

  // Voice Input (Dual-mode: Web Speech Recognition + MediaRecorder Gemini STT Fallback)
  let recognition = null;
  let isListening = false;
  let mediaRecorder = null;
  let audioChunks = [];
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  function setVoiceStatus(msg, active = true) {
    if (voiceStatusBanner) {
      if (active) voiceStatusBanner.classList.add('active');
      else voiceStatusBanner.classList.remove('active');
    }
    if (voiceStatusText) voiceStatusText.textContent = msg;
  }

  function startWebSpeech() {
    recognition = new SpeechRecognition();
    recognition.lang = 'ja-JP';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      isListening = true;
      if (micBtn) micBtn.classList.add('recording');
      setVoiceStatus('🔴 音声を認識中... お話しください (クリックで停止)');
    };

    recognition.onresult = (event) => {
      const speechResult = event.results[0][0].transcript;
      if (userChatInput) userChatInput.value = speechResult;
      setVoiceStatus(`✅ 音声認識完了: "${speechResult}"`);
      stopListening();
      setTimeout(() => {
        handleUserChat(speechResult);
      }, 400);
    };

    recognition.onerror = (event) => {
      console.warn('Web Speech error, switching to Gemini STT recorder:', event.error);
      stopListening();
      if (event.error === 'not-allowed') {
        setVoiceStatus('⚠️ マイクアクセスが拒否されています。ブラウザ設定で許可してください。');
      } else {
        startMediaRecorder();
      }
    };

    recognition.onend = () => {
      stopListening();
    };

    try {
      recognition.start();
    } catch (e) {
      console.warn('recognition.start exception:', e);
      startMediaRecorder();
    }
  }

  async function startMediaRecorder() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
        stream.getTracks().forEach(t => t.stop());
        setVoiceStatus('🤖 Google Gemini 音声モデル解析中...');
        
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = async () => {
          try {
            const resp = await fetch('/v1/mobility/stt', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                audio_base64: reader.result,
                mime_type: audioBlob.type || 'audio/webm'
              })
            });
            const sttData = await resp.json();
            if (sttData.status === 'SUCCESS' && sttData.transcript) {
              if (userChatInput) userChatInput.value = sttData.transcript;
              setVoiceStatus(`✅ Gemini認識完了: "${sttData.transcript}"`);
              setTimeout(() => {
                handleUserChat(sttData.transcript);
              }, 400);
            } else {
              setVoiceStatus('⚠️ 音声を認識できませんでした。テキストでご入力ください。');
            }
          } catch (err) {
            console.warn('Gemini STT fetch error:', err);
            setVoiceStatus('⚠️ 音声通信エラー。再度お試しください。');
          }
        };
      };

      mediaRecorder.start();
      isListening = true;
      if (micBtn) micBtn.classList.add('recording');
      setVoiceStatus('🔴 録音中(Google STT)... お話しください (クリックで送信)');
    } catch (e) {
      console.warn('getUserMedia error:', e);
      setVoiceStatus('⚠️ マイクが利用できません。テキストボックスをご利用ください。');
      stopListening();
    }
  }

  function stopListening() {
    isListening = false;
    if (micBtn) micBtn.classList.remove('recording');
    if (recognition) {
      try { recognition.stop(); } catch (e) {}
      recognition = null;
    }
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      try { mediaRecorder.stop(); } catch (e) {}
    }
    setTimeout(() => {
      if (!isListening && voiceStatusBanner) {
        voiceStatusBanner.classList.remove('active');
      }
    }, 4000);
  }

  if (micBtn) {
    micBtn.addEventListener('click', (e) => {
      e.preventDefault();
      if (isListening) {
        stopListening();
      } else {
        if (SpeechRecognition) {
          startWebSpeech();
        } else if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          startMediaRecorder();
        } else {
          alert('お使いの環境ではマイク音声入力がサポートされていません。テキストをご入力ください。');
        }
      }
    });
  }

  // Periodic polling for status and logs
  refreshStatus();
  loadTrajectory();
  setInterval(refreshStatus, 4000);
});
