/**
 * ResiliRoute 3D BCP Commander Avatar (Three.js WebGL)
 * Renders an interactive 3D officer/commander with procedural geometry,
 * lip-sync mouth animation, holographic scanning rings, and Google Cloud TTS (Japanese) playback.
 */
class CommanderAvatar {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container || typeof THREE === 'undefined') return;

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, this.container.clientWidth / this.container.clientHeight, 0.1, 100);
    this.camera.position.set(0, 0, 4.5);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.container.appendChild(this.renderer.domElement);

    this.isSpeaking = false;
    this.alertMode = false;
    this.initLights();
    this.initModel();
    this.animate();

    window.addEventListener('resize', () => this.onResize());
  }

  initLights() {
    const ambient = new THREE.AmbientLight(0xffffff, 0.8);
    this.scene.add(ambient);

    this.dirLight = new THREE.DirectionalLight(0x38bdf8, 1.8);
    this.dirLight.position.set(2, 3, 4);
    this.scene.add(this.dirLight);

    this.alertLight = new THREE.PointLight(0xef4444, 0, 10);
    this.alertLight.position.set(-2, 1, 2);
    this.scene.add(this.alertLight);
  }

  initModel() {
    this.avatarGroup = new THREE.Group();

    // 1. Torso / Uniform Armor
    const torsoGeo = new THREE.CylinderGeometry(0.85, 0.95, 1.4, 16);
    const torsoMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      metalness: 0.5,
      roughness: 0.3
    });
    const torso = new THREE.Mesh(torsoGeo, torsoMat);
    torso.position.y = -1.3;
    this.avatarGroup.add(torso);

    // Collar
    const collarGeo = new THREE.TorusGeometry(0.55, 0.1, 8, 24);
    const collarMat = new THREE.MeshStandardMaterial({ color: 0x0284c7 });
    const collar = new THREE.Mesh(collarGeo, collarMat);
    collar.rotation.x = Math.PI / 2;
    collar.position.y = -0.55;
    this.avatarGroup.add(collar);

    // 2. Head Group
    this.headGroup = new THREE.Group();

    // Head base
    const headGeo = new THREE.SphereGeometry(0.68, 32, 24);
    this.headMat = new THREE.MeshStandardMaterial({
      color: 0x334155,
      metalness: 0.3,
      roughness: 0.4
    });
    const head = new THREE.Mesh(headGeo, this.headMat);
    this.headGroup.add(head);

    // Futuristic Visor / Glass
    const visorGeo = new THREE.BoxGeometry(0.82, 0.28, 0.45);
    this.visorMat = new THREE.MeshStandardMaterial({
      color: 0x06b6d4,
      emissive: 0x0284c7,
      emissiveIntensity: 0.6,
      transparent: true,
      opacity: 0.9,
      metalness: 0.9,
      roughness: 0.1
    });
    this.visor = new THREE.Mesh(visorGeo, this.visorMat);
    this.visor.position.set(0, 0.1, 0.45);
    this.headGroup.add(this.visor);

    // Jaw / Mouth (for lip-sync)
    const mouthGeo = new THREE.BoxGeometry(0.32, 0.08, 0.1);
    this.mouthMat = new THREE.MeshStandardMaterial({
      color: 0x0ea5e9,
      emissive: 0x0284c7,
      emissiveIntensity: 0.4
    });
    this.mouth = new THREE.Mesh(mouthGeo, this.mouthMat);
    this.mouth.position.set(0, -0.32, 0.6);
    this.headGroup.add(this.mouth);

    // Headset / Antennas
    const earLeftGeo = new THREE.CylinderGeometry(0.18, 0.18, 0.15, 16);
    const earMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, metalness: 0.8 });
    const earLeft = new THREE.Mesh(earLeftGeo, earMat);
    earLeft.rotation.z = Math.PI / 2;
    earLeft.position.set(-0.72, 0.05, 0);
    this.headGroup.add(earLeft);

    const earRight = earLeft.clone();
    earRight.position.x = 0.72;
    this.headGroup.add(earRight);

    this.headGroup.position.y = 0.3;
    this.avatarGroup.add(this.headGroup);

    // Hologram Scan Ring
    const ringGeo = new THREE.RingGeometry(1.2, 1.25, 32);
    this.ringMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.5
    });
    this.scanRing = new THREE.Mesh(ringGeo, this.ringMat);
    this.scanRing.rotation.x = Math.PI / 2;
    this.scanRing.position.y = -0.5;
    this.avatarGroup.add(this.scanRing);

    this.scene.add(this.avatarGroup);
  }

  setAlert(isAlert) {
    this.alertMode = isAlert;
    if (isAlert) {
      this.visorMat.color.setHex(0xef4444);
      this.visorMat.emissive.setHex(0xdc2626);
      this.ringMat.color.setHex(0xef4444);
      this.alertLight.intensity = 2.5;
    } else {
      this.visorMat.color.setHex(0x06b6d4);
      this.visorMat.emissive.setHex(0x0284c7);
      this.ringMat.color.setHex(0x38bdf8);
      this.alertLight.intensity = 0;
    }
  }

  async speak(text, audioBase64 = null, audioMimeType = null) {
    this.isSpeaking = true;
    const bubble = document.getElementById('avatarSpeechText');
    if (bubble) bubble.textContent = text;

    // 1. If audioBase64 not provided, fetch from Google Gemini TTS / GCP TTS endpoint
    if (!audioBase64) {
      try {
        const resp = await fetch('/v1/mobility/tts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
        const d = await resp.json();
        if (d.status === 'SUCCESS' && d.audio_base64) {
          audioBase64 = d.audio_base64;
          audioMimeType = d.audio_mime_type || 'audio/wav';
        }
      } catch (e) {
        console.warn('Google TTS fetch error:', e);
      }
    }

    // 2. Play Google API Audio (Gemini Native TTS audio/wav or GCP Cloud TTS audio/mp3)
    if (audioBase64) {
      try {
        if (this.currentAudio) {
          this.currentAudio.pause();
          this.currentAudio = null;
        }

        let mime = audioMimeType || 'audio/wav';
        if (audioBase64.startsWith('UklGR')) {
          mime = 'audio/wav';
        } else if (audioBase64.startsWith('//O') || audioBase64.startsWith('SUQz')) {
          mime = 'audio/mp3';
        }

        const audio = new Audio(`data:${mime};base64,${audioBase64}`);
        this.currentAudio = audio;
        audio.onplay = () => { this.isSpeaking = true; };
        audio.onended = () => { this.isSpeaking = false; };
        audio.onerror = (err) => {
          console.warn('Google Audio playback error:', err);
          this.isSpeaking = false;
        };
        await audio.play();
        return;
      } catch (e) {
        console.warn('Audio play exception:', e);
      }
    }

    // 3. Pure visual lip-sync timer if Google audio is offline (strictly no Web Speech API generic robotic voice)
    const visualDuration = Math.min(6000, Math.max(2500, text.length * 120));
    setTimeout(() => {
      this.isSpeaking = false;
    }, visualDuration);
  }

  onResize() {
    if (!this.container) return;
    this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    const t = performance.now() * 0.002;

    // Gentle floating breathing motion
    if (this.avatarGroup) {
      this.avatarGroup.position.y = Math.sin(t * 1.5) * 0.05;
      this.headGroup.rotation.y = Math.sin(t * 0.8) * 0.08;
      this.headGroup.rotation.x = Math.cos(t * 1.1) * 0.04;
    }

    // Hologram ring rotation
    if (this.scanRing) {
      this.scanRing.rotation.z += 0.015;
    }

    // Lip sync mouth opening/closing when speaking
    if (this.mouth) {
      if (this.isSpeaking) {
        const mouthScale = 1.0 + Math.abs(Math.sin(t * 12)) * 2.8;
        this.mouth.scale.set(1, mouthScale, 1);
      } else {
        this.mouth.scale.set(1, 1, 1);
      }
    }

    // Alert strobe
    if (this.alertMode && this.alertLight) {
      this.alertLight.intensity = 1.5 + Math.sin(t * 8) * 1.2;
    }

    this.renderer.render(this.scene, this.camera);
  }
}

window.CommanderAvatar = CommanderAvatar;
