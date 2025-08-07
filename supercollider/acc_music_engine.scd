/*
ACC Telemetry Music Engine for SuperCollider
赛车遥测数据音乐生成引擎

这个SuperCollider脚本接收来自ACC遥测系统的OSC数据，
并将其转换为实时音乐，实现类似奔驰MBUX Sound Drive的功能。

使用方法：
1. 启动SuperCollider
2. 运行此脚本
3. 启动Python端的SuperColliderEngine
4. 开始驾驶ACC并享受音乐化的遥测体验
*/

(
// ============================================================================
// 全局变量和配置
// ============================================================================

// OSC接收器
~oscReceiver = nil;

// 音频合成器
~mainSynth = nil;
~rhythmSynth = nil;
~harmonySynth = nil;
~ambientSynth = nil;

// 当前音乐参数
~musicParams = (
    // 节奏参数
    bpm: 120,
    
    // 音调参数
    basePitch: 60,
    steeringInfluence: 0,
    gear: 1,
    
    // 动态参数
    volume: 0.7,
    throttle: 0,
    brake: 0,
    
    // 音色参数
    filterFreq: 1000,
    resonance: 0.3,
    
    // 空间参数
    pan: 0,
    reverb: 0.2,
    delay: 0.1
);

// 原始遥测数据
~rawData = (
    speed: 0,
    rpm: 0,
    gear: 1,
    throttle: 0,
    brake: 0,
    steer: 0
);

// ============================================================================
// 音频合成器定义
// ============================================================================

// 主引擎声音合成器
SynthDef(\accMainEngine, {
    |out=0, freq=110, amp=0.5, filterFreq=1000, resonance=0.3, pan=0|
    var sig, env, filter;
    
    // 基础引擎声音 - 使用锯齿波和噪声混合
    sig = Mix([
        Saw.ar(freq * [1, 1.01, 0.5], 0.3),
        PinkNoise.ar(0.1),
        SinOsc.ar(freq * 2, 0, 0.1)
    ]);
    
    // 动态包络
    env = EnvGen.kr(Env.asr(0.1, 1, 0.5), gate: 1);
    
    // 滤波器处理
    filter = RLPF.ar(sig, filterFreq, resonance);
    
    // 输出
    Out.ar(out, Pan2.ar(filter * env * amp, pan));
}).add;

// 节奏打击乐合成器
SynthDef(\accRhythm, {
    |out=0, freq=60, amp=0.3, decay=0.3, pan=0|
    var sig, env;
    
    // 打击乐声音
    sig = Mix([
        SinOsc.ar(freq, 0, 0.5),
        WhiteNoise.ar(0.1)
    ]);
    
    // 快速衰减包络
    env = EnvGen.kr(Env.perc(0.01, decay), doneAction: 2);
    
    // 输出
    Out.ar(out, Pan2.ar(sig * env * amp, pan));
}).add;

// 和声合成器
SynthDef(\accHarmony, {
    |out=0, freq=220, amp=0.4, filterFreq=2000, pan=0|
    var sig, env, filter;
    
    // 和声声音 - 使用多个正弦波
    sig = Mix([
        SinOsc.ar(freq * [1, 1.25, 1.5, 2], 0, [0.3, 0.2, 0.15, 0.1])
    ]);
    
    // 缓慢变化的包络
    env = EnvGen.kr(Env.asr(0.5, 1, 1), gate: 1);
    
    // 低通滤波
    filter = LPF.ar(sig, filterFreq);
    
    // 输出
    Out.ar(out, Pan2.ar(filter * env * amp, pan));
}).add;

// 环境音效合成器
SynthDef(\accAmbient, {
    |out=0, amp=0.2, reverb=0.2, delay=0.1, pan=0|
    var sig, delayed, reverbed;
    
    // 环境声音 - 使用滤波噪声
    sig = BPF.ar(PinkNoise.ar(1), LFNoise1.kr(0.1).range(200, 2000), 0.1);
    
    // 延迟效果
    delayed = DelayL.ar(sig, 1, delay) * 0.3;
    
    // 混响效果
    reverbed = FreeVerb.ar(sig + delayed, reverb, 0.8, 0.3);
    
    // 输出
    Out.ar(out, Pan2.ar(reverbed * amp, pan));
}).add;

// ============================================================================
// OSC消息处理函数
// ============================================================================

// 更新BPM
~updateBPM = { |bpm|
    ~musicParams.bpm = bpm;
    // 更新节奏模式的时间间隔
    if (~rhythmPattern.notNil) {
        ~rhythmPattern.stop;
        ~startRhythmPattern.value;
    };
};

// 更新音调参数
~updatePitch = { |basePitch, steeringInfluence, gear|
    ~musicParams.basePitch = basePitch;
    ~musicParams.steeringInfluence = steeringInfluence;
    ~musicParams.gear = gear;
    
    // 更新主合成器频率
    if (~mainSynth.notNil) {
        ~mainSynth.set(\freq, basePitch.midicps);
    };
    
    // 更新和声合成器
    if (~harmonySynth.notNil) {
        ~harmonySynth.set(\freq, (basePitch + 7).midicps); // 五度和声
    };
};

// 更新动态参数
~updateDynamics = { |volume, throttle, brake|
    ~musicParams.volume = volume;
    ~musicParams.throttle = throttle;
    ~musicParams.brake = brake;
    
    // 更新所有合成器的音量
    if (~mainSynth.notNil) {
        ~mainSynth.set(\amp, volume * 0.5);
    };
    if (~harmonySynth.notNil) {
        ~harmonySynth.set(\amp, volume * 0.3);
    };
};

// 更新音色参数
~updateTimbre = { |filterFreq, resonance|
    ~musicParams.filterFreq = filterFreq;
    ~musicParams.resonance = resonance;
    
    // 更新滤波器参数
    if (~mainSynth.notNil) {
        ~mainSynth.set(\filterFreq, filterFreq, \resonance, resonance);
    };
};

// 更新空间参数
~updateSpatial = { |pan, reverb, delay|
    ~musicParams.pan = pan;
    ~musicParams.reverb = reverb;
    ~musicParams.delay = delay;
    
    // 更新所有合成器的空间参数
    if (~mainSynth.notNil) {
        ~mainSynth.set(\pan, pan);
    };
    if (~harmonySynth.notNil) {
        ~harmonySynth.set(\pan, pan);
    };
    if (~ambientSynth.notNil) {
        ~ambientSynth.set(\reverb, reverb, \delay, delay, \pan, pan);
    };
};

// ============================================================================
// 节奏模式控制
// ============================================================================

~rhythmPattern = nil;

~startRhythmPattern = {
    var beatInterval;
    
    // 计算节拍间隔
    beatInterval = 60.0 / ~musicParams.bpm;
    
    ~rhythmPattern = Routine({
        loop {
            // 根据油门和制动创建不同的节奏模式
            var throttleIntensity = ~musicParams.throttle;
            var brakeIntensity = ~musicParams.brake;
            
            // 主节拍
            Synth(\accRhythm, [
                \freq, 60,
                \amp, 0.4 + (throttleIntensity * 0.3),
                \decay, 0.2 + (brakeIntensity * 0.3),
                \pan, ~musicParams.pan
            ]);
            
            beatInterval.wait;
            
            // 副节拍（根据转速添加）
            if (~rawData.rpm > 3000) {
                (beatInterval * 0.5).wait;
                Synth(\accRhythm, [
                    \freq, 80,
                    \amp, 0.2,
                    \decay, 0.1,
                    \pan, ~musicParams.pan * -1
                ]);
                (beatInterval * 0.5).wait;
            } else {
                beatInterval.wait;
            };
        };
    }).play;
};

// ============================================================================
// 主控制函数
// ============================================================================

~startMusicEngine = {
    "启动ACC音乐引擎...".postln;
    
    // 启动主合成器
    ~mainSynth = Synth(\accMainEngine, [
        \freq, ~musicParams.basePitch.midicps,
        \amp, ~musicParams.volume * 0.5,
        \filterFreq, ~musicParams.filterFreq,
        \resonance, ~musicParams.resonance,
        \pan, ~musicParams.pan
    ]);
    
    // 启动和声合成器
    ~harmonySynth = Synth(\accHarmony, [
        \freq, (~musicParams.basePitch + 7).midicps,
        \amp, ~musicParams.volume * 0.3,
        \filterFreq, ~musicParams.filterFreq * 1.5,
        \pan, ~musicParams.pan
    ]);
    
    // 启动环境音效
    ~ambientSynth = Synth(\accAmbient, [
        \amp, 0.2,
        \reverb, ~musicParams.reverb,
        \delay, ~musicParams.delay,
        \pan, ~musicParams.pan
    ]);
    
    // 启动节奏模式
    ~startRhythmPattern.value;
    
    "ACC音乐引擎已启动！".postln;
};

~stopMusicEngine = {
    "停止ACC音乐引擎...".postln;
    
    // 停止所有合成器
    if (~mainSynth.notNil) { ~mainSynth.free; ~mainSynth = nil; };
    if (~harmonySynth.notNil) { ~harmonySynth.free; ~harmonySynth = nil; };
    if (~ambientSynth.notNil) { ~ambientSynth.free; ~ambientSynth = nil; };
    
    // 停止节奏模式
    if (~rhythmPattern.notNil) { ~rhythmPattern.stop; ~rhythmPattern = nil; };
    
    "ACC音乐引擎已停止！".postln;
};

// ============================================================================
// OSC接收器设置
// ============================================================================

~setupOSCReceiver = {
    "设置OSC接收器...".postln;
    
    // 音乐参数OSC消息
    OSCdef(\accBPM, { |msg|
        ~updateBPM.value(msg[1]);
    }, '/acc/music/bpm');
    
    OSCdef(\accPitchBase, { |msg|
        ~updatePitch.value(msg[1], ~musicParams.steeringInfluence, ~musicParams.gear);
    }, '/acc/music/pitch/base');
    
    OSCdef(\accPitchSteering, { |msg|
        ~updatePitch.value(~musicParams.basePitch, msg[1], ~musicParams.gear);
    }, '/acc/music/pitch/steering');
    
    OSCdef(\accPitchGear, { |msg|
        ~updatePitch.value(~musicParams.basePitch, ~musicParams.steeringInfluence, msg[1]);
    }, '/acc/music/pitch/gear');
    
    OSCdef(\accVolume, { |msg|
        ~updateDynamics.value(msg[1], ~musicParams.throttle, ~musicParams.brake);
    }, '/acc/music/dynamics/volume');
    
    OSCdef(\accThrottle, { |msg|
        ~updateDynamics.value(~musicParams.volume, msg[1], ~musicParams.brake);
    }, '/acc/music/dynamics/throttle');
    
    OSCdef(\accBrake, { |msg|
        ~updateDynamics.value(~musicParams.volume, ~musicParams.throttle, msg[1]);
    }, '/acc/music/dynamics/brake');
    
    OSCdef(\accFilter, { |msg|
        ~updateTimbre.value(msg[1], ~musicParams.resonance);
    }, '/acc/music/timbre/filter');
    
    OSCdef(\accResonance, { |msg|
        ~updateTimbre.value(~musicParams.filterFreq, msg[1]);
    }, '/acc/music/timbre/resonance');
    
    OSCdef(\accPan, { |msg|
        ~updateSpatial.value(msg[1], ~musicParams.reverb, ~musicParams.delay);
    }, '/acc/music/spatial/pan');
    
    OSCdef(\accReverb, { |msg|
        ~updateSpatial.value(~musicParams.pan, msg[1], ~musicParams.delay);
    }, '/acc/music/spatial/reverb');
    
    OSCdef(\accDelay, { |msg|
        ~updateSpatial.value(~musicParams.pan, ~musicParams.reverb, msg[1]);
    }, '/acc/music/spatial/delay');
    
    // 原始遥测数据OSC消息
    OSCdef(\accRawSpeed, { |msg|
        ~rawData.speed = msg[1];
    }, '/acc/raw/speed');
    
    OSCdef(\accRawRPM, { |msg|
        ~rawData.rpm = msg[1];
    }, '/acc/raw/rpm');
    
    OSCdef(\accRawGear, { |msg|
        ~rawData.gear = msg[1];
    }, '/acc/raw/gear');
    
    OSCdef(\accRawThrottle, { |msg|
        ~rawData.throttle = msg[1];
    }, '/acc/raw/throttle');
    
    OSCdef(\accRawBrake, { |msg|
        ~rawData.brake = msg[1];
    }, '/acc/raw/brake');
    
    OSCdef(\accRawSteer, { |msg|
        ~rawData.steer = msg[1];
    }, '/acc/raw/steer');
    
    "OSC接收器已设置完成！监听端口: 57120".postln;
};

// ============================================================================
// 清理函数
// ============================================================================

~cleanup = {
    "清理ACC音乐引擎资源...".postln;
    
    // 停止音乐引擎
    ~stopMusicEngine.value;
    
    // 清理OSC定义
    OSCdef.freeAll;
    
    "清理完成！".postln;
};

// ============================================================================
// 用户界面和控制
// ============================================================================

~showStatus = {
    "\n=== ACC音乐引擎状态 ===".postln;
    "当前BPM: %".format(~musicParams.bpm).postln;
    "基础音调: % (MIDI)".format(~musicParams.basePitch).postln;
    "音量: %".format(~musicParams.volume).postln;
    "滤波频率: % Hz".format(~musicParams.filterFreq).postln;
    "立体声平衡: %".format(~musicParams.pan).postln;
    "\n原始数据:".postln;
    "速度: % km/h".format(~rawData.speed).postln;
    "转速: % RPM".format(~rawData.rpm).postln;
    "档位: %".format(~rawData.gear).postln;
    "油门: %".format(~rawData.throttle).postln;
    "制动: %".format(~rawData.brake).postln;
    "转向: %".format(~rawData.steer).postln;
    "========================\n".postln;
};

// ============================================================================
// 主程序启动
// ============================================================================

"\n🎵 ACC Telemetry Music Engine 🏎️".postln;
"====================================".postln;
"正在初始化...".postln;

// 等待服务器启动
Server.default.waitForBoot({
    // 设置OSC接收器
    ~setupOSCReceiver.value;
    
    // 启动音乐引擎
    ~startMusicEngine.value;
    
    "\n🎉 ACC音乐引擎已就绪！".postln;
    "\n使用说明:".postln;
    "1. 启动Python端的SuperColliderEngine".postln;
    "2. 运行ACC游戏".postln;
    "3. 享受音乐化的驾驶体验！".postln;
    "\n控制命令:".postln;
    "~showStatus.value;  // 显示当前状态".postln;
    "~stopMusicEngine.value;  // 停止音乐引擎".postln;
    "~startMusicEngine.value;  // 重新启动音乐引擎".postln;
    "~cleanup.value;  // 清理所有资源".postln;
    "\n准备接收遥测数据...".postln;
});

// 注册清理函数，在退出时自动调用
CmdPeriod.doOnce({ ~cleanup.value; });

)

// ============================================================================
// 使用示例和测试代码
// ============================================================================

/*
// 手动测试音乐参数（在没有遥测数据时使用）
(
// 测试BPM变化
fork {
    (60..180).do { |bpm|
        ~updateBPM.value(bpm);
        "BPM: %".format(bpm).postln;
        0.1.wait;
    };
};
)

// 测试音调变化
(
fork {
    (48..72).do { |pitch|
        ~updatePitch.value(pitch, 0, 1);
        "Pitch: %".format(pitch).postln;
        0.2.wait;
    };
};
)

// 测试转向效果
(
fork {
    100.do {
        var steering = sin(Date.getDate.rawSeconds * 2) * 0.5;
        ~updatePitch.value(60, steering, 1);
        ~updateSpatial.value(steering, 0.2, 0.1);
        0.05.wait;
    };
};
)
*/