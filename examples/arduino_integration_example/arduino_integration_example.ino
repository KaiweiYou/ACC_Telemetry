/*
 * ACC_Telemetry Arduino集成示例
 * 
 * 这个示例展示了如何将ACC遥测数据与Arduino集成，
 * 用于驱动物理仪表盘、LED指示灯或其他硬件设备。
 * 
 * 硬件要求:
 * - Arduino Uno/Mega/Nano等
 * - 可选：LED灯、舵机电机、LCD显示屏等
 * 
 * 连接方式:
 * - 通过USB串口连接到运行ACC_Telemetry的电脑
 * 
 * 使用方法:
 * 1. 将此代码上传到Arduino
 * 2. 运行配套的Python脚本arduino_serial_bridge.py
 */

// 引入必要的库
#include <Servo.h>  // 用于控制舵机（模拟指针）

// 定义引脚
#define RPM_LED_PIN_1 3  // RPM LED 1
#define RPM_LED_PIN_2 4  // RPM LED 2
#define RPM_LED_PIN_3 5  // RPM LED 3
#define RPM_LED_PIN_4 6  // RPM LED 4
#define RPM_LED_PIN_5 7  // RPM LED 5

#define SPEED_SERVO_PIN 9  // 速度表舵机

// 创建舵机对象
Servo speedServo;  // 速度表指针

// 数据缓冲区
const int BUFFER_SIZE = 64;
char inputBuffer[BUFFER_SIZE];
int bufferIndex = 0;

// 遥测数据
float speed = 0.0;
int rpm = 0;
int gear = 0;
float throttle = 0.0;
float brake = 0.0;

// 最大值设置
const int MAX_RPM = 9000;  // 最大转速
const int RPM_THRESHOLD = MAX_RPM / 5;  // 每个LED的转速阈值

void setup() {
  // 初始化串口通信
  Serial.begin(115200);
  
  // 初始化LED引脚
  pinMode(RPM_LED_PIN_1, OUTPUT);
  pinMode(RPM_LED_PIN_2, OUTPUT);
  pinMode(RPM_LED_PIN_3, OUTPUT);
  pinMode(RPM_LED_PIN_4, OUTPUT);
  pinMode(RPM_LED_PIN_5, OUTPUT);
  
  // 初始化舵机
  speedServo.attach(SPEED_SERVO_PIN);
  speedServo.write(0);  // 初始位置
  
  // 发送就绪消息
  Serial.println("Arduino ready");
}

void loop() {
  // 读取串口数据
  readSerialData();
  
  // 更新输出设备
  updateRpmLeds();
  updateSpeedGauge();
  
  // 短暂延迟
  delay(10);
}

// 读取串口数据
void readSerialData() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    
    // 如果收到换行符，处理完整的命令
    if (c == '\n') {
      inputBuffer[bufferIndex] = '\0';  // 添加字符串结束符
      parseCommand(inputBuffer);
      bufferIndex = 0;  // 重置缓冲区索引
    } 
    // 否则将字符添加到缓冲区
    else if (bufferIndex < BUFFER_SIZE - 1) {
      inputBuffer[bufferIndex++] = c;
    }
  }
}

// 解析命令
void parseCommand(char* command) {
  // 命令格式: "S:123.4,R:5678,G:2,T:0.75,B:0.25"
  // S=速度, R=转速, G=档位, T=油门, B=刹车
  
  char* token = strtok(command, ",");
  while (token != NULL) {
    // 检查命令前缀
    if (token[0] == 'S' && token[1] == ':') {
      speed = atof(token + 2);
    }
    else if (token[0] == 'R' && token[1] == ':') {
      rpm = atoi(token + 2);
    }
    else if (token[0] == 'G' && token[1] == ':') {
      gear = atoi(token + 2);
    }
    else if (token[0] == 'T' && token[1] == ':') {
      throttle = atof(token + 2);
    }
    else if (token[0] == 'B' && token[1] == ':') {
      brake = atof(token + 2);
    }
    
    // 获取下一个令牌
    token = strtok(NULL, ",");
  }
  
  // 发送确认
  Serial.print("ACK:S=");
  Serial.print(speed);
  Serial.print(",R=");
  Serial.print(rpm);
  Serial.print(",G=");
  Serial.println(gear);
}

// 更新RPM LED指示灯
void updateRpmLeds() {
  // 根据转速点亮相应的LED
  digitalWrite(RPM_LED_PIN_1, rpm > RPM_THRESHOLD * 1 ? HIGH : LOW);
  digitalWrite(RPM_LED_PIN_2, rpm > RPM_THRESHOLD * 2 ? HIGH : LOW);
  digitalWrite(RPM_LED_PIN_3, rpm > RPM_THRESHOLD * 3 ? HIGH : LOW);
  digitalWrite(RPM_LED_PIN_4, rpm > RPM_THRESHOLD * 4 ? HIGH : LOW);
  digitalWrite(RPM_LED_PIN_5, rpm > RPM_THRESHOLD * 5 ? HIGH : LOW);
}

// 更新速度表
void updateSpeedGauge() {
  // 将速度映射到舵机角度（0-180度）
  // 假设最大速度为300km/h
  int angle = map(constrain(speed, 0, 300), 0, 300, 0, 180);
  speedServo.write(angle);
}