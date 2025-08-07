import json
import threading
import time
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from ..core.telemetry import ACCTelemetry
import os

class WebTelemetryServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.app = Flask(__name__, 
                        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                        static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        self.app.config['SECRET_KEY'] = 'acc_telemetry_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 初始化遥测数据读取器
        self.telemetry = ACCTelemetry()
        
        # 加载显示设置
        self.load_display_settings()
        
        # 数据更新线程控制
        self.running = False
        self.update_thread = None
        
        # 设置路由
        self.setup_routes()
        
    def load_display_settings(self):
        """加载显示设置"""
        settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "telemetry_display_settings.json")
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    self.display_settings = json.load(f)
            else:
                # 默认显示基础数据
                self.display_settings = {
                    "speed": True,
                    "rpm": True,
                    "gear": True,
                    "fuel": True,
                    "throttle": True,
                    "brake": True,
                    "clutch": True,
                    "tire_pressure_fl": True,
                    "tire_pressure_fr": True,
                    "tire_pressure_rl": True,
                    "tire_pressure_rr": True
                }
        except Exception as e:
            print(f"加载设置失败: {e}")
            self.display_settings = {}
    
    def setup_routes(self):
        """设置Web路由"""
        @self.app.route('/')
        def index():
            return render_template('dashboard.html')
        
        @self.app.route('/api/config')
        def get_config():
            """获取显示配置"""
            return jsonify({
                'display_settings': self.display_settings,
                'data_config': self.get_data_config()
            })
        
        @self.socketio.on('connect')
        def handle_connect():
            print('客户端已连接')
            emit('connected', {'data': '连接成功'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('客户端已断开连接')
    
    def get_data_config(self):
        """获取数据项配置"""
        return {
            # 基础数据
            'speed': {'label': '速度', 'unit': 'km/h', 'category': '基础数据'},
            'rpm': {'label': '转速', 'unit': 'RPM', 'category': '基础数据'},
            'gear': {'label': '档位', 'unit': '', 'category': '基础数据'},
            'fuel': {'label': '燃油', 'unit': 'L', 'category': '基础数据'},
            
            # 踏板数据
            'throttle': {'label': '油门', 'unit': '%', 'category': '踏板数据'},
            'brake': {'label': '刹车', 'unit': '%', 'category': '踏板数据'},
            'clutch': {'label': '离合', 'unit': '%', 'category': '踏板数据'},
            
            # 轮胎压力
            'tire_pressure_fl': {'label': '轮胎压力-左前', 'unit': 'PSI', 'category': '轮胎压力'},
            'tire_pressure_fr': {'label': '轮胎压力-右前', 'unit': 'PSI', 'category': '轮胎压力'},
            'tire_pressure_rl': {'label': '轮胎压力-左后', 'unit': 'PSI', 'category': '轮胎压力'},
            'tire_pressure_rr': {'label': '轮胎压力-右后', 'unit': 'PSI', 'category': '轮胎压力'},
            
            # 轮胎温度
            'tire_temp_fl': {'label': '轮胎温度-左前', 'unit': '°C', 'category': '轮胎温度'},
            'tire_temp_fr': {'label': '轮胎温度-右前', 'unit': '°C', 'category': '轮胎温度'},
            'tire_temp_rl': {'label': '轮胎温度-左后', 'unit': '°C', 'category': '轮胎温度'},
            'tire_temp_rr': {'label': '轮胎温度-右后', 'unit': '°C', 'category': '轮胎温度'},
            
            # 刹车温度
            'brake_temp_fl': {'label': '刹车温度-左前', 'unit': '°C', 'category': '刹车温度'},
            'brake_temp_fr': {'label': '刹车温度-右前', 'unit': '°C', 'category': '刹车温度'},
            'brake_temp_rl': {'label': '刹车温度-左后', 'unit': '°C', 'category': '刹车温度'},
            'brake_temp_rr': {'label': '刹车温度-右后', 'unit': '°C', 'category': '刹车温度'},
            
            # 车辆动态
            'acceleration_x': {'label': '横向G力', 'unit': 'G', 'category': '车辆动态'},
            'acceleration_y': {'label': '纵向G力', 'unit': 'G', 'category': '车辆动态'},
            'acceleration_z': {'label': '垂直G力', 'unit': 'G', 'category': '车辆动态'},
            'steer_angle': {'label': '转向角度', 'unit': '°', 'category': '车辆动态'},
            
            # 引擎数据
            'engine_temp': {'label': '水温', 'unit': '°C', 'category': '引擎数据'},
            'turbo_boost': {'label': '涡轮增压', 'unit': 'bar', 'category': '引擎数据'},
            
            # 车轮滑移
            'wheel_slip_fl': {'label': '车轮滑移-左前', 'unit': '', 'category': '车轮滑移'},
            'wheel_slip_fr': {'label': '车轮滑移-右前', 'unit': '', 'category': '车轮滑移'},
            'wheel_slip_rl': {'label': '车轮滑移-左后', 'unit': '', 'category': '车轮滑移'},
            'wheel_slip_rr': {'label': '车轮滑移-右后', 'unit': '', 'category': '车轮滑移'},
            
            # 辅助系统
            'drs': {'label': 'DRS状态', 'unit': '', 'category': '辅助系统'},
            'tc': {'label': '牵引力控制', 'unit': '', 'category': '辅助系统'},
            'abs': {'label': 'ABS状态', 'unit': '', 'category': '辅助系统'},
            
            # 圈速数据
            'lap_time': {'label': '当前圈时间', 'unit': 'ms', 'category': '圈速数据'},
            'last_lap': {'label': '上一圈时间', 'unit': 'ms', 'category': '圈速数据'},
            'best_lap': {'label': '最佳圈时间', 'unit': 'ms', 'category': '圈速数据'}
        }
    
    def format_telemetry_data(self, data):
        """格式化遥测数据"""
        if data is None:
            return None
        
        formatted_data = {}
        data_config = self.get_data_config()
        
        for field in self.display_settings:
            if self.display_settings.get(field, False):
                try:
                    value = getattr(data, field)
                    
                    # 根据数据类型格式化显示
                    if field == 'gear':
                        # 档位特殊处理
                        if value == 0:
                            formatted_data[field] = "R"
                        elif value == 1:
                            formatted_data[field] = "N"
                        else:
                            formatted_data[field] = str(value - 1)
                    elif field in ['throttle', 'brake', 'clutch']:
                        # 踏板数据转换为百分比
                        formatted_data[field] = f"{value * 100:.0f}%"
                    elif field in ['drs', 'tc', 'abs']:
                        # 布尔状态显示
                        formatted_data[field] = "开启" if value else "关闭"
                    elif field in ['lap_time', 'last_lap', 'best_lap']:
                        # 时间数据转换为秒
                        if value > 0:
                            seconds = value / 1000
                            minutes = int(seconds // 60)
                            seconds = seconds % 60
                            formatted_data[field] = f"{minutes}:{seconds:06.3f}"
                        else:
                            formatted_data[field] = "--:---.---"
                    elif isinstance(value, float):
                        # 浮点数保留适当小数位
                        if field in ['acceleration_x', 'acceleration_y', 'acceleration_z']:
                            formatted_data[field] = f"{value:.2f}"
                        elif field in ['wheel_slip_fl', 'wheel_slip_fr', 'wheel_slip_rl', 'wheel_slip_rr']:
                            formatted_data[field] = f"{value:.3f}"
                        else:
                            formatted_data[field] = f"{value:.1f}"
                    else:
                        # 整数或其他类型
                        formatted_data[field] = str(value)
                        
                except AttributeError:
                    formatted_data[field] = "N/A"
                except Exception as e:
                    formatted_data[field] = "Error"
        
        return formatted_data
    
    def update_data_loop(self):
        """数据更新循环"""
        while self.running:
            try:
                data = self.telemetry.get_telemetry()
                formatted_data = self.format_telemetry_data(data)
                
                if formatted_data:
                    self.socketio.emit('telemetry_update', formatted_data)
                
                time.sleep(1/60)  # 60fps更新频率
            except Exception as e:
                print(f"数据更新错误: {e}")
                time.sleep(0.1)
    
    def start(self):
        """启动Web服务器"""
        self.running = True
        self.update_thread = threading.Thread(target=self.update_data_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        print(f"Web遥测面板启动在 http://{self.host}:{self.port}")
        print(f"局域网访问地址: http://[您的IP地址]:{self.port}")
        
        self.socketio.run(self.app, host=self.host, port=self.port, debug=False)
    
    def stop(self):
        """停止Web服务器"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()

if __name__ == '__main__':
    server = WebTelemetryServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        server.stop()