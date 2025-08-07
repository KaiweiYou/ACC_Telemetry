from pythonosc.udp_client import SimpleUDPClient
from ..core.telemetry import ACCTelemetry, TelemetryData
import time
import math
import threading
from typing import Dict, Any, Optional, Callable
import logging

# 配置日志
logger = logging.getLogger(__name__)

class SuperColliderEngine:
    """SuperCollider音频引擎接口
    
    负责将ACC遥测数据转换为音乐参数，并通过OSC协议发送到SuperCollider
    实现类似奔驰MBUX Sound Drive的功能
    """
    
    def __init__(self, sc_ip="127.0.0.1", sc_port=57120, update_rate=60, telemetry_source=None):
        """初始化SuperCollider引擎
        
        Args:
            sc_ip: SuperCollider服务器IP地址
            sc_port: SuperCollider服务器端口 (默认57120)
            update_rate: 数据更新频率 (Hz)
            telemetry_source: 外部遥测数据源，如果为None则创建内部实例
        """
        self.sc_ip = sc_ip
        self.sc_port = sc_port
        self.update_rate = update_rate
        
        # 创建OSC客户端
        self.osc_client = SimpleUDPClient(sc_ip, sc_port)
        
        # 使用外部遥测数据源或创建内部实例
        if telemetry_source is not None:
            self.telemetry = telemetry_source
            self._owns_telemetry = False  # 标记不拥有遥测实例
        else:
            self.telemetry = ACCTelemetry()
            self._owns_telemetry = True   # 标记拥有遥测实例
        
        # 运行状态控制
        self.running = False
        self.update_thread = None
        
        # 数据映射配置
        self.mapping_config = self._init_mapping_config()
        
        # 数据平滑处理
        self.smoothing_factors = {
            'speed': 0.1,
            'rpm': 0.15,
            'acceleration': 0.2,
            'steering': 0.1,
            'brake': 0.05
        }
        
        # 上一帧数据用于平滑处理
        self.previous_data = {}
        
        logger.info(f"SuperCollider引擎已初始化 - 目标: {sc_ip}:{sc_port}")
    
    def _init_mapping_config(self) -> Dict[str, Dict[str, Any]]:
        """初始化数据映射配置
        
        定义遥测数据到音乐参数的映射关系
        """
        return {
            # 主节奏控制 - 基于速度和引擎转速
            'rhythm': {
                'bpm_base': 120,  # 基础BPM
                'bpm_range': (80, 180),  # BPM范围
                'speed_influence': 0.6,  # 速度对BPM的影响权重
                'rpm_influence': 0.4,   # 转速对BPM的影响权重
            },
            
            # 音调和和声 - 基于转向和档位
            'harmony': {
                'base_note': 60,  # 基础音符 (C4)
                'scale_type': 'major',  # 音阶类型
                'steering_range': 12,  # 转向影响的半音范围
                'gear_intervals': [0, 2, 4, 5, 7, 9, 11],  # 各档位对应的音程
            },
            
            # 音量和强度 - 基于加速度和制动
            'dynamics': {
                'base_volume': 0.7,  # 基础音量
                'acceleration_boost': 0.3,  # 加速时的音量提升
                'brake_reduction': 0.5,  # 制动时的音量衰减
                'throttle_influence': 0.4,  # 油门对音量的影响
            },
            
            # 音色和滤波 - 基于引擎温度和轮胎状态
            'timbre': {
                'filter_base': 1000,  # 基础滤波频率
                'temp_influence': 2000,  # 温度对滤波的影响范围
                'tire_pressure_influence': 500,  # 轮胎压力对音色的影响
                'resonance_base': 0.3,  # 基础共振
            },
            
            # 空间效果 - 基于车辆动态
            'spatial': {
                'reverb_base': 0.2,  # 基础混响
                'lateral_g_influence': 0.3,  # 横向G力对立体声的影响
                'delay_base': 0.1,  # 基础延迟
            }
        }
    
    def _smooth_value(self, key: str, current_value: float, smoothing_factor: float = None) -> float:
        """数据平滑处理
        
        Args:
            key: 数据键名
            current_value: 当前值
            smoothing_factor: 平滑因子 (0-1, 越小越平滑)
            
        Returns:
            平滑后的值
        """
        if smoothing_factor is None:
            smoothing_factor = self.smoothing_factors.get(key, 0.1)
        
        if key not in self.previous_data:
            self.previous_data[key] = current_value
            return current_value
        
        # 指数移动平均
        smoothed = (smoothing_factor * current_value + 
                   (1 - smoothing_factor) * self.previous_data[key])
        self.previous_data[key] = smoothed
        return smoothed
    
    def _map_to_bpm(self, data: TelemetryData) -> float:
        """将遥测数据映射为BPM
        
        Args:
            data: 遥测数据
            
        Returns:
            计算得出的BPM值
        """
        config = self.mapping_config['rhythm']
        
        # 速度归一化 (假设最大速度300km/h)
        speed_norm = min(data.speed / 300.0, 1.0)
        
        # 转速归一化 (假设最大转速8000rpm)
        rpm_norm = min(data.rpm / 8000.0, 1.0)
        
        # 计算BPM
        bpm_factor = (speed_norm * config['speed_influence'] + 
                     rpm_norm * config['rpm_influence'])
        
        bpm = (config['bpm_base'] + 
               bpm_factor * (config['bpm_range'][1] - config['bpm_range'][0]))
        
        return self._smooth_value('bpm', bpm)
    
    def _map_to_pitch(self, data: TelemetryData) -> Dict[str, float]:
        """将遥测数据映射为音调参数
        
        Args:
            data: 遥测数据
            
        Returns:
            包含音调参数的字典
        """
        config = self.mapping_config['harmony']
        
        # 转向角度影响音调 (-1到1的范围)
        steering_norm = max(-1.0, min(1.0, data.steer_angle))
        pitch_offset = steering_norm * config['steering_range']
        
        # 档位影响基础音调
        gear_offset = 0
        if 0 <= data.gear < len(config['gear_intervals']):
            gear_offset = config['gear_intervals'][data.gear]
        
        base_pitch = config['base_note'] + gear_offset + pitch_offset
        
        return {
            'base_pitch': self._smooth_value('pitch', base_pitch),
            'steering_influence': steering_norm,
            'gear': data.gear
        }
    
    def _map_to_dynamics(self, data: TelemetryData) -> Dict[str, float]:
        """将遥测数据映射为动态参数
        
        Args:
            data: 遥测数据
            
        Returns:
            包含动态参数的字典
        """
        config = self.mapping_config['dynamics']
        
        # 基础音量
        volume = config['base_volume']
        
        # 油门影响
        throttle_boost = data.throttle * config['throttle_influence']
        
        # 加速度影响 (纵向G力)
        accel_boost = max(0, data.acceleration_y) * config['acceleration_boost']
        
        # 制动影响
        brake_reduction = data.brake * config['brake_reduction']
        
        final_volume = max(0.1, min(1.0, volume + throttle_boost + accel_boost - brake_reduction))
        
        return {
            'volume': self._smooth_value('volume', final_volume),
            'throttle': data.throttle,
            'brake': data.brake,
            'acceleration': data.acceleration_y
        }
    
    def _map_to_timbre(self, data: TelemetryData) -> Dict[str, float]:
        """将遥测数据映射为音色参数
        
        Args:
            data: 遥测数据
            
        Returns:
            包含音色参数的字典
        """
        config = self.mapping_config['timbre']
        
        # 引擎温度影响滤波器频率
        temp_norm = min(data.engine_temp / 120.0, 1.0)  # 假设最高温度120°C
        filter_freq = config['filter_base'] + temp_norm * config['temp_influence']
        
        # 轮胎压力平均值影响共振
        avg_tire_pressure = (data.tire_pressure_fl + data.tire_pressure_fr + 
                           data.tire_pressure_rl + data.tire_pressure_rr) / 4.0
        pressure_norm = min(avg_tire_pressure / 3.0, 1.0)  # 假设最大压力3.0bar
        resonance = config['resonance_base'] + pressure_norm * 0.4
        
        return {
            'filter_freq': self._smooth_value('filter', filter_freq),
            'resonance': resonance,
            'engine_temp': data.engine_temp,
            'tire_pressure_avg': avg_tire_pressure
        }
    
    def _map_to_spatial(self, data: TelemetryData) -> Dict[str, float]:
        """将遥测数据映射为空间音效参数
        
        Args:
            data: 遥测数据
            
        Returns:
            包含空间参数的字典
        """
        config = self.mapping_config['spatial']
        
        # 横向G力影响立体声平衡
        lateral_g = max(-1.0, min(1.0, data.acceleration_x))
        pan = lateral_g  # -1(左) 到 1(右)
        
        # 速度影响混响深度
        speed_norm = min(data.speed / 200.0, 1.0)
        reverb = config['reverb_base'] + speed_norm * 0.3
        
        # 转向影响延迟时间
        steering_abs = abs(data.steer_angle)
        delay = config['delay_base'] + steering_abs * 0.2
        
        return {
            'pan': pan,
            'reverb': reverb,
            'delay': delay,
            'lateral_g': data.acceleration_x
        }
    
    def _send_music_data(self, data: TelemetryData) -> None:
        """发送音乐数据到SuperCollider
        
        Args:
            data: 遥测数据
        """
        try:
            # 映射各种音乐参数
            bpm = self._map_to_bpm(data)
            pitch_params = self._map_to_pitch(data)
            dynamics_params = self._map_to_dynamics(data)
            timbre_params = self._map_to_timbre(data)
            spatial_params = self._map_to_spatial(data)
            
            # 发送节奏参数
            self.osc_client.send_message("/acc/music/bpm", bpm)
            
            # 发送音调参数
            self.osc_client.send_message("/acc/music/pitch/base", pitch_params['base_pitch'])
            self.osc_client.send_message("/acc/music/pitch/steering", pitch_params['steering_influence'])
            self.osc_client.send_message("/acc/music/pitch/gear", pitch_params['gear'])
            
            # 发送动态参数
            self.osc_client.send_message("/acc/music/dynamics/volume", dynamics_params['volume'])
            self.osc_client.send_message("/acc/music/dynamics/throttle", dynamics_params['throttle'])
            self.osc_client.send_message("/acc/music/dynamics/brake", dynamics_params['brake'])
            
            # 发送音色参数
            self.osc_client.send_message("/acc/music/timbre/filter", timbre_params['filter_freq'])
            self.osc_client.send_message("/acc/music/timbre/resonance", timbre_params['resonance'])
            
            # 发送空间参数
            self.osc_client.send_message("/acc/music/spatial/pan", spatial_params['pan'])
            self.osc_client.send_message("/acc/music/spatial/reverb", spatial_params['reverb'])
            self.osc_client.send_message("/acc/music/spatial/delay", spatial_params['delay'])
            
            # 发送原始遥测数据（供高级用户使用）
            self.osc_client.send_message("/acc/raw/speed", data.speed)
            self.osc_client.send_message("/acc/raw/rpm", data.rpm)
            self.osc_client.send_message("/acc/raw/gear", data.gear)
            self.osc_client.send_message("/acc/raw/throttle", data.throttle)
            self.osc_client.send_message("/acc/raw/brake", data.brake)
            self.osc_client.send_message("/acc/raw/steer", data.steer_angle)
            
        except Exception as e:
            logger.error(f"发送音乐数据时出错: {e}")
    
    def _update_loop(self) -> None:
        """数据更新循环"""
        logger.info("音乐生成循环已启动")
        
        while self.running:
            try:
                # 读取遥测数据
                telemetry_data = self.telemetry.get_telemetry()
                
                if telemetry_data is not None:
                    # 发送音乐数据
                    self._send_music_data(telemetry_data)
                
                # 控制更新频率
                time.sleep(1.0 / self.update_rate)
                
            except Exception as e:
                logger.error(f"更新循环中出错: {e}")
                time.sleep(0.1)  # 出错时短暂暂停
        
        logger.info("音乐生成循环已停止")
    
    def start(self) -> bool:
        """启动音乐生成引擎
        
        Returns:
            bool: 启动是否成功
        """
        if self.running:
            logger.warning("音乐生成引擎已在运行")
            return True
        
        try:
            # 只有当拥有遥测实例时才需要连接
            if self._owns_telemetry:
                if not self.telemetry.connect():
                    logger.error("无法连接到ACC遥测系统")
                    return False
            
            self.running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
            logger.info("SuperCollider音乐生成引擎已启动")
            return True
            
        except Exception as e:
            logger.error(f"启动音乐生成引擎时发生错误: {e}")
            self.running = False
            return False
    
    def stop(self) -> None:
        """停止音乐生成引擎"""
        if not self.running:
            logger.warning("音乐生成引擎未在运行")
            return
        
        self.running = False
        
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2.0)
        
        logger.info("SuperCollider音乐生成引擎已停止")
    
    def is_running(self) -> bool:
        """检查音乐生成引擎是否正在运行
        
        Returns:
            bool: 引擎运行状态
        """
        return self.running
    
    def update_parameters(self, music_params: Dict[str, Any]) -> None:
        """更新音乐参数
        
        Args:
            music_params: 音乐参数字典
        """
        try:
            # 发送BPM参数
            if 'bpm' in music_params:
                self.osc_client.send_message("/acc/music/bpm", music_params['bpm'])
            
            # 发送音调参数
            if 'pitch' in music_params:
                pitch_data = music_params['pitch']
                if isinstance(pitch_data, dict):
                    self.osc_client.send_message("/acc/music/pitch/base", pitch_data.get('base', 60))
                    self.osc_client.send_message("/acc/music/pitch/steering", pitch_data.get('steering_influence', 0))
                    self.osc_client.send_message("/acc/music/pitch/gear", pitch_data.get('gear', 1))
                else:
                    self.osc_client.send_message("/acc/music/pitch/base", pitch_data)
            
            # 发送动态参数
            if 'dynamics' in music_params:
                dynamics_data = music_params['dynamics']
                if isinstance(dynamics_data, dict):
                    self.osc_client.send_message("/acc/music/dynamics/volume", dynamics_data.get('volume', 0.7))
                    self.osc_client.send_message("/acc/music/dynamics/throttle", dynamics_data.get('throttle', 0))
                    self.osc_client.send_message("/acc/music/dynamics/brake", dynamics_data.get('brake', 0))
            
            # 发送音色参数
            if 'timbre' in music_params:
                timbre_data = music_params['timbre']
                if isinstance(timbre_data, dict):
                    self.osc_client.send_message("/acc/music/timbre/filter", timbre_data.get('filter_freq', 1000))
                    self.osc_client.send_message("/acc/music/timbre/resonance", timbre_data.get('resonance', 0.3))
            
            # 发送空间参数
            if 'spatial' in music_params:
                spatial_data = music_params['spatial']
                if isinstance(spatial_data, dict):
                    self.osc_client.send_message("/acc/music/spatial/pan", spatial_data.get('pan', 0))
                    self.osc_client.send_message("/acc/music/spatial/reverb", spatial_data.get('reverb', 0.2))
                    self.osc_client.send_message("/acc/music/spatial/delay", spatial_data.get('delay', 0.1))
                    
        except Exception as e:
            logger.error(f"更新音乐参数时出错: {e}")
    
    def send_raw_data(self, raw_data: Dict[str, Any]) -> None:
        """发送原始遥测数据
        
        Args:
            raw_data: 原始数据字典
        """
        try:
            # 发送原始遥测数据（供高级用户使用）
            for key, value in raw_data.items():
                self.osc_client.send_message(f"/acc/raw/{key}", value)
                
        except Exception as e:
            logger.error(f"发送原始数据时出错: {e}")
    
    def update_mapping_config(self, new_config: Dict[str, Any]) -> None:
        """更新映射配置
        
        Args:
            new_config: 新的映射配置
        """
        self.mapping_config.update(new_config)
        logger.info("映射配置已更新")
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态信息
        
        Returns:
            包含状态信息的字典
        """
        return {
            'running': self.running,
            'sc_address': f"{self.sc_ip}:{self.sc_port}",
            'update_rate': self.update_rate,
            'mapping_config': self.mapping_config
        }
    
    def close(self) -> None:
        """关闭引擎并清理资源"""
        self.stop()
        # 只有当拥有遥测实例时才关闭连接
        if self._owns_telemetry:
            self.telemetry.close()
        logger.info("SuperCollider引擎已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


if __name__ == "__main__":
    # 示例用法
    with SuperColliderEngine() as engine:
        engine.start()
        
        try:
            print("SuperCollider音乐生成引擎正在运行...")
            print("按Ctrl+C停止")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止引擎...")