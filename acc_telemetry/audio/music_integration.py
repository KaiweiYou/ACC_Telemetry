#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACC遥测音乐集成模块

这个模块将ACC遥测数据与SuperCollider音乐引擎集成，
实现实时的音乐化驾驶体验。

作者: Assistant
日期: 2024
"""

import threading
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .supercollider_engine import SuperColliderEngine
from ..core.telemetry import ACCTelemetry, TelemetryData


@dataclass
class MusicConfig:
    """音乐生成配置类"""
    # OSC配置
    osc_host: str = "127.0.0.1"
    osc_port: int = 57120  # SuperCollider默认端口
    
    # 更新频率
    update_rate: int = 60  # Hz
    
    # 音乐参数范围
    bpm_range: tuple = (80, 180)
    pitch_range: tuple = (36, 84)  # MIDI音符范围
    volume_range: tuple = (0.1, 1.0)
    filter_range: tuple = (200, 8000)  # Hz
    
    # 数据映射敏感度
    speed_sensitivity: float = 1.0
    rpm_sensitivity: float = 1.0
    steering_sensitivity: float = 1.0
    pedal_sensitivity: float = 1.0
    
    # 平滑参数
    smoothing_factor: float = 0.1
    
    # 启用的音乐元素
    enable_rhythm: bool = True
    enable_harmony: bool = True
    enable_dynamics: bool = True
    enable_timbre: bool = True
    enable_spatial: bool = True


class MusicIntegration:
    """ACC遥测音乐集成主类"""
    
    def __init__(self, config: Optional[MusicConfig] = None):
        """
        初始化音乐集成系统
        
        Args:
            config: 音乐配置对象，如果为None则使用默认配置
        """
        self.config = config or MusicConfig()
        self.logger = logging.getLogger(__name__)
        
        # 初始化共享的遥测数据源
        self.telemetry = ACCTelemetry()
        
        # 初始化音乐引擎，传入共享的遥测数据源
        self.music_engine = SuperColliderEngine(
            sc_ip=self.config.osc_host,
            sc_port=self.config.osc_port,
            update_rate=self.config.update_rate,
            telemetry_source=self.telemetry  # 传入共享的遥测数据源
        )
        
        # 运行状态
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # 数据缓存
        self._last_data: Optional[TelemetryData] = None
        self._music_state: Dict[str, Any] = {
            'bpm': 120,
            'base_pitch': 60,
            'volume': 0.7,
            'filter_freq': 1000,
            'pan': 0.0
        }
        
        self.logger.info("音乐集成系统已初始化")
    
    def start(self) -> bool:
        """
        启动音乐集成系统
        
        Returns:
            bool: 启动是否成功
        """
        if self._running:
            self.logger.warning("音乐集成系统已在运行")
            return True
        
        try:
            # 启动遥测系统（共享数据源）
            if not self.telemetry.connect():
                self.logger.error("无法连接到ACC遥测数据")
                return False
            
            # 启动音乐引擎（使用共享的遥测数据源）
            if not self.music_engine.start():
                self.logger.error("无法启动SuperCollider音乐引擎")
                self.telemetry.close()
                return False
            
            # 启动主循环线程
            self._running = True
            self._thread = threading.Thread(target=self._main_loop, daemon=True)
            self._thread.start()
            
            self.logger.info("音乐集成系统已启动")
            return True
            
        except Exception as e:
            self.logger.error(f"启动音乐集成系统时发生错误: {e}")
            self.stop()
            return False
    
    def stop(self):
        """
        停止音乐集成系统
        """
        if not self._running:
            return
        
        self.logger.info("正在停止音乐集成系统...")
        
        # 停止主循环
        self._running = False
        
        # 等待线程结束
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        
        # 停止组件
        self.music_engine.stop()
        self.telemetry.close()
        
        self.logger.info("音乐集成系统已停止")
    
    def _main_loop(self):
        """
        主数据处理循环
        """
        update_interval = 1.0 / self.config.update_rate
        
        self.logger.info(f"开始音乐数据处理循环，更新频率: {self.config.update_rate}Hz")
        
        while self._running:
            try:
                start_time = time.time()
                
                # 读取遥测数据
                telemetry_data = self.telemetry.read_data()
                
                if telemetry_data:
                    # 处理音乐数据
                    self._process_music_data(telemetry_data)
                    self._last_data = telemetry_data
                
                # 控制更新频率
                elapsed = time.time() - start_time
                sleep_time = max(0, update_interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"音乐数据处理循环中发生错误: {e}")
                time.sleep(0.1)  # 避免错误循环
    
    def _process_music_data(self, data: TelemetryData):
        """
        处理遥测数据并生成音乐参数
        
        Args:
            data: 遥测数据对象
        """
        try:
            # 计算音乐参数
            music_params = self._calculate_music_parameters(data)
            
            # 发送到音乐引擎
            self.music_engine.update_parameters(music_params)
            
            # 发送原始数据
            raw_data = {
                'speed': data.speed,
                'rpm': data.rpm,
                'gear': data.gear,
                'throttle': data.throttle,
                'brake': data.brake,
                'steer': data.steer_angle
            }
            self.music_engine.send_raw_data(raw_data)
            
        except Exception as e:
            self.logger.error(f"处理音乐数据时发生错误: {e}")
    
    def _calculate_music_parameters(self, data: TelemetryData) -> Dict[str, Any]:
        """
        根据遥测数据计算音乐参数
        
        Args:
            data: 遥测数据对象
            
        Returns:
            Dict[str, Any]: 音乐参数字典
        """
        params = {}
        
        # 节奏参数 - 基于速度和转速
        if self.config.enable_rhythm:
            # 速度影响BPM (0-300 km/h -> 80-180 BPM)
            speed_factor = min(data.speed / 300.0, 1.0) * self.config.speed_sensitivity
            bpm = self.config.bpm_range[0] + speed_factor * (self.config.bpm_range[1] - self.config.bpm_range[0])
            
            # 转速影响节奏复杂度 (通过BPM微调)
            rpm_factor = min(data.rpm / 8000.0, 1.0) * self.config.rpm_sensitivity
            bpm += rpm_factor * 20  # 最多增加20 BPM
            
            params['bpm'] = max(self.config.bpm_range[0], min(self.config.bpm_range[1], bpm))
        
        # 和声参数 - 基于转向和档位
        if self.config.enable_harmony:
            # 基础音调 (C4 = 60)
            base_pitch = 60
            
            # 转向影响音调偏移 (-1到1 -> -12到+12半音)
            steering_offset = data.steer_angle * 12 * self.config.steering_sensitivity
            
            # 档位影响音调高度 (1-8档 -> 0-14半音)
            gear_offset = max(0, data.gear - 1) * 2
            
            final_pitch = base_pitch + steering_offset + gear_offset
            params['pitch'] = {
                'base': max(self.config.pitch_range[0], min(self.config.pitch_range[1], final_pitch)),
                'steering_influence': data.steer_angle * self.config.steering_sensitivity,
                'gear': data.gear
            }
        
        # 动态参数 - 基于油门和制动
        if self.config.enable_dynamics:
            # 基础音量
            base_volume = 0.7
            
            # 油门增加音量
            throttle_boost = data.throttle * 0.3 * self.config.pedal_sensitivity
            
            # 制动改变音色特性（不直接影响音量）
            brake_factor = data.brake * self.config.pedal_sensitivity
            
            volume = base_volume + throttle_boost
            params['dynamics'] = {
                'volume': max(self.config.volume_range[0], min(self.config.volume_range[1], volume)),
                'throttle': data.throttle,
                'brake': data.brake
            }
        
        # 音色参数 - 基于引擎温度和轮胎压力
        if self.config.enable_timbre:
            # 引擎温度影响滤波频率 (50-120°C -> 200-8000Hz)
            temp_factor = max(0, min(1, (data.engine_temp - 50) / 70))
            filter_freq = self.config.filter_range[0] + temp_factor * (self.config.filter_range[1] - self.config.filter_range[0])
            
            # 轮胎压力影响共振 (平均压力)
            avg_tire_pressure = (data.tire_pressure_fl + data.tire_pressure_fr + 
                               data.tire_pressure_rl + data.tire_pressure_rr) / 4
            # 正常压力范围 25-35 PSI -> 共振 0.1-0.8
            resonance = max(0.1, min(0.8, (avg_tire_pressure - 25) / 10 * 0.7 + 0.1))
            
            params['timbre'] = {
                'filter_freq': filter_freq,
                'resonance': resonance
            }
        
        # 空间参数 - 基于横向G力
        if self.config.enable_spatial:
            # 横向G力影响立体声平衡 (-3G到+3G -> -1到+1)
            lateral_g = data.acceleration_x  # 使用横向加速度
            pan = max(-1, min(1, lateral_g / 3.0))
            
            # 速度影响混响和延迟
            speed_factor = min(data.speed / 200.0, 1.0)
            reverb = 0.1 + speed_factor * 0.3  # 0.1-0.4
            delay = 0.05 + speed_factor * 0.15  # 0.05-0.2秒
            
            params['spatial'] = {
                'pan': pan,
                'reverb': reverb,
                'delay': delay
            }
        
        return params
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取系统状态信息
        
        Returns:
            Dict[str, Any]: 状态信息字典
        """
        return {
            'running': self._running,
            'telemetry_connected': self.telemetry.is_connected(),
            'music_engine_running': self.music_engine.is_running(),
            'last_data_time': getattr(self._last_data, 'timestamp', None) if self._last_data else None,
            'music_state': self._music_state.copy(),
            'config': {
                'update_rate': self.config.update_rate,
                'osc_host': self.config.osc_host,
                'osc_port': self.config.osc_port
            }
        }
    
    def update_config(self, new_config: MusicConfig):
        """
        更新配置（需要重启系统才能生效）
        
        Args:
            new_config: 新的配置对象
        """
        self.config = new_config
        self.logger.info("音乐配置已更新，重启系统后生效")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


# 便捷函数
def create_music_integration(config: Optional[MusicConfig] = None) -> MusicIntegration:
    """
    创建音乐集成系统实例
    
    Args:
        config: 可选的配置对象
        
    Returns:
        MusicIntegration: 音乐集成系统实例
    """
    return MusicIntegration(config)


if __name__ == "__main__":
    # 测试代码
    import logging
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建自定义配置
    config = MusicConfig(
        update_rate=30,  # 降低更新频率用于测试
        speed_sensitivity=1.2,
        steering_sensitivity=0.8
    )
    
    # 创建并运行音乐集成系统
    with create_music_integration(config) as music_system:
        try:
            print("音乐集成系统正在运行...")
            print("按 Ctrl+C 停止")
            
            while True:
                status = music_system.get_status()
                print(f"\r状态: 运行={status['running']}, "
                      f"遥测={status['telemetry_connected']}, "
                      f"音乐引擎={status['music_engine_running']}", end="")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n正在停止音乐集成系统...")
    
    print("音乐集成系统已停止")