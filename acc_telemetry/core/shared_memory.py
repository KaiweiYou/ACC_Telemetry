from __future__ import annotations

import copy
import mmap
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional


class SharedMemoryTimeout(Exception):
    pass


class ACC_STATUS(Enum):

    ACC_OFF = 0
    ACC_REPLAY = 1
    ACC_LIVE = 2
    ACC_PAUSE = 3


class ACC_SESSION_TYPE(Enum):

    ACC_UNKNOW = -1
    ACC_PRACTICE = 0
    ACC_QUALIFY = 1
    ACC_RACE = 2
    ACC_HOTLAP = 3
    ACC_TIME_ATTACK = 4
    ACC_DRIFT = 5
    ACC_DRAG = 6
    ACC_HOTSTINT = 7
    ACC_HOTLAPSUPERPOLE = 8

    def __str__(self) -> str:

        if self == ACC_SESSION_TYPE.ACC_PRACTICE:
            string = "Practice"

        elif self == ACC_SESSION_TYPE.ACC_QUALIFY:
            string = "Qualify"

        elif self == ACC_SESSION_TYPE.ACC_RACE:
            string = "Race"

        elif self == ACC_SESSION_TYPE.ACC_HOTLAP:
            string = "Hotlap"

        elif self == ACC_SESSION_TYPE.ACC_TIME_ATTACK:
            string = "Time_Attack"

        elif self == ACC_SESSION_TYPE.ACC_DRIFT:
            string = "Drift"

        elif self == ACC_SESSION_TYPE.ACC_DRAG:
            string = "Drag"

        elif self == ACC_SESSION_TYPE.ACC_HOTSTINT:
            string = "Hotstint"

        elif self == ACC_SESSION_TYPE.ACC_HOTLAPSUPERPOLE:
            string = "Superpole"

        else:
            string = "Unknow"

        return string


class ACC_FLAG_TYPE(Enum):

    ACC_NO_FLAG = 0
    ACC_BLUE_FLAG = 1
    ACC_YELLOW_FLAG = 2
    ACC_BLACK_FLAG = 3
    ACC_WHITE_FLAG = 4
    ACC_CHECKERED_FLAG = 5
    ACC_PENALTY_FLAG = 6
    ACC_GREEN_FLAG = 7
    ACC_ORANGE_FLAG = 8


class ACC_PENALTY_TYPE(Enum):

    """
    Wrong way is 22 now ?
    What's 18 then ?
    Are there any other non documented enums ... ?
    """

    UnknownValue = -1
    No_penalty = 0
    DriveThrough_Cutting = 1
    StopAndGo_10_Cutting = 2
    StopAndGo_20_Cutting = 3
    StopAndGo_30_Cutting = 4
    Disqualified_Cutting = 5
    RemoveBestLaptime_Cutting = 6

    DriveThrough_PitSpeeding = 7
    StopAndGo_10_PitSpeeding = 8
    StopAndGo_20_PitSpeeding = 9
    StopAndGo_30_PitSpeeding = 10
    Disqualified_PitSpeeding = 11
    RemoveBestLaptime_PitSpeeding = 12

    Disqualified_IgnoredMandatoryPit = 13

    PostRaceTime = 14
    Disqualified_Trolling = 15
    Disqualified_PitEntry = 16
    Disqualified_PitExit = 17
    Disqualified_WrongWay_old = 18

    DriveThrough_IgnoredDriverStint = 19
    Disqualified_IgnoredDriverStint = 20

    Disqualified_ExceededDriverStintLimit = 21
    Disqualified_WrongWay = 22


class ACC_TRACK_GRIP_STATUS(Enum):

    ACC_GREEN = 0
    ACC_FAST = 1
    ACC_OPTIMUM = 2
    ACC_GREASY = 3
    ACC_DAMP = 4
    ACC_WET = 5
    ACC_FLOODED = 6

    def __str__(self) -> str:

        if self == ACC_TRACK_GRIP_STATUS.ACC_GREEN:
            string = "Green"

        elif self == ACC_TRACK_GRIP_STATUS.ACC_FAST:
            string = "Fast"

        elif self == ACC_TRACK_GRIP_STATUS.ACC_OPTIMUM:
            string = "Optimum"

        elif self == ACC_TRACK_GRIP_STATUS.ACC_GREASY:
            string = "Greasy"

        elif self == ACC_TRACK_GRIP_STATUS.ACC_DAMP:
            string = "Damp"

        elif self == ACC_TRACK_GRIP_STATUS.ACC_WET:
            string = "Wet"

        elif self == ACC_TRACK_GRIP_STATUS.ACC_FLOODED:
            string = "Flooded"

        return string


class ACC_RAIN_INTENSITY(Enum):

    ACC_NO_RAIN = 0
    ACC_DRIZZLE = 1
    ACC_LIGHT_RAIN = 2
    ACC_MEDIUM_RAIN = 3
    ACC_HEAVY_RAIN = 4
    ACC_THUNDERSTORM = 5

    def __str__(self) -> str:

        if self == ACC_RAIN_INTENSITY.ACC_NO_RAIN:
            string = "No Rain"

        elif self == ACC_RAIN_INTENSITY.ACC_DRIZZLE:
            string = "Drizzle"

        elif self == ACC_RAIN_INTENSITY.ACC_LIGHT_RAIN:
            string = "Light Rain"

        elif self == ACC_RAIN_INTENSITY.ACC_MEDIUM_RAIN:
            string = "Medium Rain"

        elif self == ACC_RAIN_INTENSITY.ACC_HEAVY_RAIN:
            string = "Heavy rain"

        elif self == ACC_RAIN_INTENSITY.ACC_THUNDERSTORM:
            string = "Thunderstorm"

        return string


@dataclass
class Vector3f:
    x: float
    y: float
    z: float

    def __str__(self) -> str:
        return f"x: {self.x}, y: {self.y}, z: {self.z}"


@dataclass
class Wheels:
    front_left: float
    front_right: float
    rear_left: float
    rear_right: float

    def __str__(self) -> str:
        return f"FL: {self.front_left}\nFR: {self.front_right}\
            \nRL: {self.rear_left}\nRR: {self.rear_right}"


@dataclass
class ContactPoint:
    front_left: Vector3f
    front_right: Vector3f
    rear_left: Vector3f
    rear_right: Vector3f

    @staticmethod
    def from_list(points: List[List[float]]) -> Any:
        fl = Vector3f(*points[0])
        fr = Vector3f(*points[1])
        rl = Vector3f(*points[2])
        rr = Vector3f(*points[3])

        return ContactPoint(fl, fr, rl, rr)

    def __str__(self) -> str:
        return f"FL: {self.front_left},\nFR: {self.front_right},\
            \nRL: {self.rear_left},\nRR: {self.rear_right}"


@dataclass
class CarDamage:
    front: float
    rear: float
    left: float
    right: float
    center: float  # Center is actually the sum of all


@dataclass
class PhysicsMap:

    packed_id: int
    gas: float
    brake: float
    fuel: float
    gear: int
    rpm: int
    steer_angle: float
    speed_kmh: float
    velocity: Vector3f
    g_force: Vector3f

    wheel_slip: Wheels
    wheel_pressure: Wheels
    wheel_angular_s: Wheels
    tyre_core_temp: Wheels

    suspension_travel: Wheels

    tc: float
    heading: float
    pitch: float
    roll: float
    car_damage: CarDamage
    pit_limiter_on: bool
    abs: float

    autoshifter_on: bool
    turbo_boost: float

    air_temp: float
    road_temp: float
    local_angular_vel: Vector3f
    final_ff: float

    brake_temp: Wheels
    clutch: float

    is_ai_controlled: bool

    tyre_contact_point: ContactPoint
    tyre_contact_normal: ContactPoint
    tyre_contact_heading: ContactPoint

    brake_bias: float

    local_velocity: Vector3f

    slip_ratio: Wheels
    slip_angle: Wheels

    suspension_damage: Wheels
    water_temp: float

    brake_pressure: Wheels
    front_brake_compound: int
    rear_brake_compound: int
    pad_life: Wheels
    disc_life: Wheels

    ignition_on: bool
    starter_engine_on: bool
    is_engine_running: bool

    kerb_vibration: float
    slip_vibration: float
    g_vibration: float
    abs_vibration: float

    @staticmethod
    def is_equal(a: PhysicsMap, b: PhysicsMap) -> bool:
        """
        Since I won't check every single attribute,
        comparing suspension_travel is a good alternative
        since there is always a bit of oscillation in the
        suspension when the car is possessed by the player.

        Parameters:
        a: PhysicsMap
        b: PhysicsMap

        Return:
        result: bool
        """

        return a.suspension_travel == b.suspension_travel


@dataclass
class GraphicsMap:

    packed_id: int
    status: ACC_STATUS
    session_type: ACC_SESSION_TYPE
    current_time_str: str
    last_time_str: str
    best_time_str: str
    last_sector_time_str: str
    completed_lap: int
    position: int
    current_time: int
    last_time: int
    best_time: int
    session_time_left: float
    distance_traveled: float
    is_in_pit: bool
    current_sector_index: int
    last_sector_time: int
    number_of_laps: int
    tyre_compound: str
    normalized_car_position: float
    active_cars: int
    car_coordinates: List[Vector3f]
    car_id: List[int]
    player_car_id: int
    penalty_time: float
    flag: ACC_FLAG_TYPE
    penalty: ACC_PENALTY_TYPE
    ideal_line_on: bool
    is_in_pit_lane: bool
    mandatory_pit_done: bool
    wind_speed: float
    wind_direction: float
    is_setup_menu_visible: bool
    main_display_index: int
    secondary_display_index: int
    tc_level: int
    tc_cut_level: int
    engine_map: int
    abs_level: int
    fuel_per_lap: float
    rain_light: bool
    flashing_light: bool
    light_stage: int
    exhaust_temp: float
    wiper_stage: int
    driver_stint_total_time_left: int
    driver_stint_time_left: int
    rain_tyres: bool
    session_index: int
    used_fuel: float
    delta_lap_time_str: str
    delta_lap_time: int
    estimated_lap_time_str: str
    estimated_lap_time: int
    is_delta_positive: bool
    is_valid_lap: bool
    fuel_estimated_laps: float
    track_status: str
    missing_mandatory_pits: int
    clock: float
    direction_light_left: bool
    direction_light_right: bool
    global_yellow: bool
    global_yellow_s1: bool
    global_yellow_s2: bool
    global_yellow_s3: bool
    global_white: bool
    global_green: bool
    global_chequered: bool
    global_red: bool
    mfd_tyre_set: int
    mfd_fuel_to_add: float
    mfd_tyre_pressure: Wheels
    track_grip_status: ACC_TRACK_GRIP_STATUS
    rain_intensity: ACC_RAIN_INTENSITY
    rain_intensity_in_10min: ACC_RAIN_INTENSITY
    rain_intensity_in_30min: ACC_RAIN_INTENSITY
    current_tyre_set: int
    strategy_tyre_set: int
    gap_ahead: int
    gap_behind: int


@dataclass
class StaticsMap:

    sm_version: str
    ac_version: str
    number_of_session: int
    num_cars: int
    car_model: str
    track: str
    player_name: str
    player_surname: str
    player_nick: str
    sector_count: int
    max_rpm: int
    max_fuel: float
    penalty_enabled: bool
    aid_fuel_rate: float
    aid_tyre_rate: float
    aid_mechanical_damage: float
    aid_stability: float
    aid_auto_clutch: bool
    pit_window_start: int
    pit_window_end: int
    is_online: bool
    dry_tyres_name: str
    wet_tyres_name: str


@dataclass
class ACC_map:

    Physics: PhysicsMap
    Graphics: GraphicsMap
    Static: StaticsMap


class accSM(mmap.mmap):

    def unpack_value(self, offset: int, fmt: str) -> Any:
        """
        Unpack a single value from the shared memory.

        Parameters:
        offset: int
            The offset in the shared memory.
        fmt: str
            The format of the value to unpack.

        Return:
        result: Any
            The unpacked value.
        """

        size = struct.calcsize(fmt)
        self.seek(offset)
        value = struct.unpack(fmt, self.read(size))[0]

        return value

    def unpack_array(self, offset: int, fmt: str, count: int) -> List[Any]:
        """
        Unpack an array of values from the shared memory.

        Parameters:
        offset: int
            The offset in the shared memory.
        fmt: str
            The format of the values to unpack.
        count: int
            The number of values to unpack.

        Return:
        result: List[Any]
            The unpacked values.
        """

        size = struct.calcsize(fmt)
        self.seek(offset)
        values = []

        for _ in range(count):
            values.append(struct.unpack(fmt, self.read(size))[0])

        return values

    def unpack_array2D(self, offset: int, fmt: str, count: int, count2: int) -> List[List[Any]]:
        """
        Unpack a 2D array of values from the shared memory.

        Parameters:
        offset: int
            The offset in the shared memory.
        fmt: str
            The format of the values to unpack.
        count: int
            The number of values to unpack in the first dimension.
        count2: int
            The number of values to unpack in the second dimension.

        Return:
        result: List[List[Any]]
            The unpacked values.
        """

        size = struct.calcsize(fmt)
        self.seek(offset)
        values = []

        for _ in range(count):
            values2 = []
            for _ in range(count2):
                values2.append(struct.unpack(fmt, self.read(size))[0])
            values.append(values2)

        return values

    def unpack_string(self, offset: int, max_len: int) -> str:
        """
        Unpack a string from the shared memory.

        Parameters:
        offset: int
            The offset in the shared memory.
        max_len: int
            The maximum length of the string.

        Return:
        result: str
            The unpacked string.
        """

        self.seek(offset)
        result = self.read(max_len).decode("utf-8")

        if "\x00" in result:
            result = result.split("\x00")[0]

        return result


def read_physic_map(accSM: accSM) -> PhysicsMap:
    """
    Read the physics map from the shared memory.

    Parameters:
    accSM: accSM
        The shared memory object.

    Return:
    result: PhysicsMap
        The physics map.
    """

    # Read the packed ID
    packed_id = accSM.unpack_value(0, "i")

    # Read the gas value
    gas = accSM.unpack_value(4, "f")

    # Read the brake value
    brake = accSM.unpack_value(8, "f")

    # Read the fuel value
    fuel = accSM.unpack_value(12, "f")

    # Read the gear value
    gear = accSM.unpack_value(16, "i")

    # Read the rpm value
    rpm = accSM.unpack_value(20, "i")

    # Read the steer angle value
    steer_angle = accSM.unpack_value(24, "f")

    # Read the speed value
    speed_kmh = accSM.unpack_value(28, "f")

    # Read the velocity value
    velocity_x = accSM.unpack_value(32, "f")
    velocity_y = accSM.unpack_value(36, "f")
    velocity_z = accSM.unpack_value(40, "f")
    velocity = Vector3f(velocity_x, velocity_y, velocity_z)

    # Read the g force value
    g_force_x = accSM.unpack_value(44, "f")
    g_force_y = accSM.unpack_value(48, "f")
    g_force_z = accSM.unpack_value(52, "f")
    g_force = Vector3f(g_force_x, g_force_y, g_force_z)

    # Read the wheel slip value
    wheel_slip_fl = accSM.unpack_value(56, "f")
    wheel_slip_fr = accSM.unpack_value(60, "f")
    wheel_slip_rl = accSM.unpack_value(64, "f")
    wheel_slip_rr = accSM.unpack_value(68, "f")
    wheel_slip = Wheels(wheel_slip_fl, wheel_slip_fr, wheel_slip_rl, wheel_slip_rr)

    # Read the wheel load value
    # Field is not used by ACC
    _ = accSM.unpack_value(72, "f")
    _ = accSM.unpack_value(76, "f")
    _ = accSM.unpack_value(80, "f")
    _ = accSM.unpack_value(84, "f")

    # Read the wheel pressure value
    wheel_pressure_fl = accSM.unpack_value(88, "f")
    wheel_pressure_fr = accSM.unpack_value(92, "f")
    wheel_pressure_rl = accSM.unpack_value(96, "f")
    wheel_pressure_rr = accSM.unpack_value(100, "f")
    wheel_pressure = Wheels(
        wheel_pressure_fl, wheel_pressure_fr, wheel_pressure_rl, wheel_pressure_rr
    )

    # Read the wheel angular speed value
    wheel_angular_speed_fl = accSM.unpack_value(104, "f")
    wheel_angular_speed_fr = accSM.unpack_value(108, "f")
    wheel_angular_speed_rl = accSM.unpack_value(112, "f")
    wheel_angular_speed_rr = accSM.unpack_value(116, "f")
    wheel_angular_speed = Wheels(
        wheel_angular_speed_fl,
        wheel_angular_speed_fr,
        wheel_angular_speed_rl,
        wheel_angular_speed_rr,
    )

    # Read the tyre wear value
    # Field is not used by ACC
    _ = accSM.unpack_value(120, "f")
    _ = accSM.unpack_value(124, "f")
    _ = accSM.unpack_value(128, "f")
    _ = accSM.unpack_value(132, "f")

    # Read the tyre dirty level value
    # Field is not used by ACC
    _ = accSM.unpack_value(136, "f")
    _ = accSM.unpack_value(140, "f")
    _ = accSM.unpack_value(144, "f")
    _ = accSM.unpack_value(148, "f")

    # Read the tyre core temperature value
    tyre_core_temp_fl = accSM.unpack_value(152, "f")
    tyre_core_temp_fr = accSM.unpack_value(156, "f")
    tyre_core_temp_rl = accSM.unpack_value(160, "f")
    tyre_core_temp_rr = accSM.unpack_value(164, "f")
    tyre_core_temp = Wheels(
        tyre_core_temp_fl, tyre_core_temp_fr, tyre_core_temp_rl, tyre_core_temp_rr
    )

    # Read the camber rad value
    # Field is not used by ACC
    _ = accSM.unpack_value(168, "f")
    _ = accSM.unpack_value(172, "f")
    _ = accSM.unpack_value(176, "f")
    _ = accSM.unpack_value(180, "f")

    # Read the suspension travel value
    suspension_travel_fl = accSM.unpack_value(184, "f")
    suspension_travel_fr = accSM.unpack_value(188, "f")
    suspension_travel_rl = accSM.unpack_value(192, "f")
    suspension_travel_rr = accSM.unpack_value(196, "f")
    suspension_travel = Wheels(
        suspension_travel_fl,
        suspension_travel_fr,
        suspension_travel_rl,
        suspension_travel_rr,
    )

    # Read the drs value
    # Field is not used by ACC
    _ = accSM.unpack_value(200, "i")

    # Read the tc value
    tc = accSM.unpack_value(204, "f")

    # Read the heading value
    heading = accSM.unpack_value(208, "f")

    # Read the pitch value
    pitch = accSM.unpack_value(212, "f")

    # Read the roll value
    roll = accSM.unpack_value(216, "f")

    # Read the car damage value
    car_damage_front = accSM.unpack_value(220, "f")
    car_damage_rear = accSM.unpack_value(224, "f")
    car_damage_left = accSM.unpack_value(228, "f")
    car_damage_right = accSM.unpack_value(232, "f")
    car_damage_center = accSM.unpack_value(236, "f")
    car_damage = CarDamage(
        car_damage_front,
        car_damage_rear,
        car_damage_left,
        car_damage_right,
        car_damage_center,
    )

    # Read the pit limiter on value
    pit_limiter_on = accSM.unpack_value(240, "i") == 1

    # Read the abs value
    abs_value = accSM.unpack_value(244, "f")

    # Read the autoshifter on value
    autoshifter_on = accSM.unpack_value(248, "i") == 1

    # Read the turbo boost value
    turbo_boost = accSM.unpack_value(252, "f")

    # Read the air temp value
    air_temp = accSM.unpack_value(256, "f")

    # Read the road temp value
    road_temp = accSM.unpack_value(260, "f")

    # Read the local angular velocity value
    local_angular_vel_x = accSM.unpack_value(264, "f")
    local_angular_vel_y = accSM.unpack_value(268, "f")
    local_angular_vel_z = accSM.unpack_value(272, "f")
    local_angular_vel = Vector3f(
        local_angular_vel_x, local_angular_vel_y, local_angular_vel_z
    )

    # Read the final ff value
    final_ff = accSM.unpack_value(276, "f")

    # Read the performance meter value
    # Field is not used by ACC
    _ = accSM.unpack_value(280, "f")

    # Read the engine brake value
    # Field is not used by ACC
    _ = accSM.unpack_value(284, "i")

    # Read the ers recovery level value
    # Field is not used by ACC
    _ = accSM.unpack_value(288, "i")

    # Read the ers power level value
    # Field is not used by ACC
    _ = accSM.unpack_value(292, "i")

    # Read the ers heat charging value
    # Field is not used by ACC
    _ = accSM.unpack_value(296, "i")

    # Read the ers is charging value
    # Field is not used by ACC
    _ = accSM.unpack_value(300, "i")

    # Read the kers input value
    # Field is not used by ACC
    _ = accSM.unpack_value(304, "f")

    # Read the clutch value
    # Field is not used by ACC
    _ = accSM.unpack_value(308, "f")

    # Read the tyre temp value
    # Field is not used by ACC
    _ = accSM.unpack_value(312, "f")
    _ = accSM.unpack_value(316, "f")
    _ = accSM.unpack_value(320, "f")
    _ = accSM.unpack_value(324, "f")

    # Read the brake temp value
    brake_temp_fl = accSM.unpack_value(328, "f")
    brake_temp_fr = accSM.unpack_value(332, "f")
    brake_temp_rl = accSM.unpack_value(336, "f")
    brake_temp_rr = accSM.unpack_value(340, "f")
    brake_temp = Wheels(brake_temp_fl, brake_temp_fr, brake_temp_rl, brake_temp_rr)

    # Read the clutch value
    clutch = accSM.unpack_value(344, "f")

    # Read the is ai controlled value
    is_ai_controlled = accSM.unpack_value(348, "i") == 1

    # Read the tyre contact point value
    tyre_contact_point_fl_x = accSM.unpack_value(352, "f")
    tyre_contact_point_fl_y = accSM.unpack_value(356, "f")
    tyre_contact_point_fl_z = accSM.unpack_value(360, "f")
    tyre_contact_point_fl = Vector3f(
        tyre_contact_point_fl_x, tyre_contact_point_fl_y, tyre_contact_point_fl_z
    )

    tyre_contact_point_fr_x = accSM.unpack_value(364, "f")
    tyre_contact_point_fr_y = accSM.unpack_value(368, "f")
    tyre_contact_point_fr_z = accSM.unpack_value(372, "f")
    tyre_contact_point_fr = Vector3f(
        tyre_contact_point_fr_x, tyre_contact_point_fr_y, tyre_contact_point_fr_z
    )

    tyre_contact_point_rl_x = accSM.unpack_value(376, "f")
    tyre_contact_point_rl_y = accSM.unpack_value(380, "f")
    tyre_contact_point_rl_z = accSM.unpack_value(384, "f")
    tyre_contact_point_rl = Vector3f(
        tyre_contact_point_rl_x, tyre_contact_point_rl_y, tyre_contact_point_rl_z
    )

    tyre_contact_point_rr_x = accSM.unpack_value(388, "f")
    tyre_contact_point_rr_y = accSM.unpack_value(392, "f")
    tyre_contact_point_rr_z = accSM.unpack_value(396, "f")
    tyre_contact_point_rr = Vector3f(
        tyre_contact_point_rr_x, tyre_contact_point_rr_y, tyre_contact_point_rr_z
    )

    tyre_contact_point = ContactPoint(
        tyre_contact_point_fl,
        tyre_contact_point_fr,
        tyre_contact_point_rl,
        tyre_contact_point_rr,
    )

    # Read the tyre contact normal value
    tyre_contact_normal_fl_x = accSM.unpack_value(400, "f")
    tyre_contact_normal_fl_y = accSM.unpack_value(404, "f")
    tyre_contact_normal_fl_z = accSM.unpack_value(408, "f")
    tyre_contact_normal_fl = Vector3f(
        tyre_contact_normal_fl_x, tyre_contact_normal_fl_y, tyre_contact_normal_fl_z
    )

    tyre_contact_normal_fr_x = accSM.unpack_value(412, "f")
    tyre_contact_normal_fr_y = accSM.unpack_value(416, "f")
    tyre_contact_normal_fr_z = accSM.unpack_value(420, "f")
    tyre_contact_normal_fr = Vector3f(
        tyre_contact_normal_fr_x, tyre_contact_normal_fr_y, tyre_contact_normal_fr_z
    )

    tyre_contact_normal_rl_x = accSM.unpack_value(424, "f")
    tyre_contact_normal_rl_y = accSM.unpack_value(428, "f")
    tyre_contact_normal_rl_z = accSM.unpack_value(432, "f")
    tyre_contact_normal_rl = Vector3f(
        tyre_contact_normal_rl_x, tyre_contact_normal_rl_y, tyre_contact_normal_rl_z
    )

    tyre_contact_normal_rr_x = accSM.unpack_value(436, "f")
    tyre_contact_normal_rr_y = accSM.unpack_value(440, "f")
    tyre_contact_normal_rr_z = accSM.unpack_value(444, "f")
    tyre_contact_normal_rr = Vector3f(
        tyre_contact_normal_rr_x, tyre_contact_normal_rr_y, tyre_contact_normal_rr_z
    )

    tyre_contact_normal = ContactPoint(
        tyre_contact_normal_fl,
        tyre_contact_normal_fr,
        tyre_contact_normal_rl,
        tyre_contact_normal_rr,
    )

    # Read the tyre contact heading value
    tyre_contact_heading_fl_x = accSM.unpack_value(448, "f")
    tyre_contact_heading_fl_y = accSM.unpack_value(452, "f")
    tyre_contact_heading_fl_z = accSM.unpack_value(456, "f")
    tyre_contact_heading_fl = Vector3f(
        tyre_contact_heading_fl_x, tyre_contact_heading_fl_y, tyre_contact_heading_fl_z
    )

    tyre_contact_heading_fr_x = accSM.unpack_value(460, "f")
    tyre_contact_heading_fr_y = accSM.unpack_value(464, "f")
    tyre_contact_heading_fr_z = accSM.unpack_value(468, "f")
    tyre_contact_heading_fr = Vector3f(
        tyre_contact_heading_fr_x, tyre_contact_heading_fr_y, tyre_contact_heading_fr_z
    )

    tyre_contact_heading_rl_x = accSM.unpack_value(472, "f")
    tyre_contact_heading_rl_y = accSM.unpack_value(476, "f")
    tyre_contact_heading_rl_z = accSM.unpack_value(480, "f")
    tyre_contact_heading_rl = Vector3f(
        tyre_contact_heading_rl_x, tyre_contact_heading_rl_y, tyre_contact_heading_rl_z
    )

    tyre_contact_heading_rr_x = accSM.unpack_value(484, "f")
    tyre_contact_heading_rr_y = accSM.unpack_value(488, "f")
    tyre_contact_heading_rr_z = accSM.unpack_value(492, "f")
    tyre_contact_heading_rr = Vector3f(
        tyre_contact_heading_rr_x, tyre_contact_heading_rr_y, tyre_contact_heading_rr_z
    )

    tyre_contact_heading = ContactPoint(
        tyre_contact_heading_fl,
        tyre_contact_heading_fr,
        tyre_contact_heading_rl,
        tyre_contact_heading_rr,
    )

    # Read the brake bias value
    brake_bias = accSM.unpack_value(496, "f")

    # Read the local velocity value
    local_velocity_x = accSM.unpack_value(500, "f")
    local_velocity_y = accSM.unpack_value(504, "f")
    local_velocity_z = accSM.unpack_value(508, "f")
    local_velocity = Vector3f(local_velocity_x, local_velocity_y, local_velocity_z)

    # Read the P2P activation value
    # Field is not used by ACC
    _ = accSM.unpack_value(512, "i")

    # Read the P2P status value
    # Field is not used by ACC
    _ = accSM.unpack_value(516, "i")

    # Read the current max rpm value
    # Field is not used by ACC
    _ = accSM.unpack_value(520, "i")

    # Read the mz value
    # Field is not used by ACC
    _ = accSM.unpack_value(524, "f")
    _ = accSM.unpack_value(528, "f")
    _ = accSM.unpack_value(532, "f")
    _ = accSM.unpack_value(536, "f")

    # Read the fx value
    # Field is not used by ACC
    _ = accSM.unpack_value(540, "f")
    _ = accSM.unpack_value(544, "f")
    _ = accSM.unpack_value(548, "f")
    _ = accSM.unpack_value(552, "f")

    # Read the fy value
    # Field is not used by ACC
    _ = accSM.unpack_value(556, "f")
    _ = accSM.unpack_value(560, "f")
    _ = accSM.unpack_value(564, "f")
    _ = accSM.unpack_value(568, "f")

    # Read the slip ratio value
    slip_ratio_fl = accSM.unpack_value(572, "f")
    slip_ratio_fr = accSM.unpack_value(576, "f")
    slip_ratio_rl = accSM.unpack_value(580, "f")
    slip_ratio_rr = accSM.unpack_value(584, "f")
    slip_ratio = Wheels(slip_ratio_fl, slip_ratio_fr, slip_ratio_rl, slip_ratio_rr)

    # Read the slip angle value
    slip_angle_fl = accSM.unpack_value(588, "f")
    slip_angle_fr = accSM.unpack_value(592, "f")
    slip_angle_rl = accSM.unpack_value(596, "f")
    slip_angle_rr = accSM.unpack_value(600, "f")
    slip_angle = Wheels(slip_angle_fl, slip_angle_fr, slip_angle_rl, slip_angle_rr)

    # Read the tcinaction value
    # Field is not used by ACC
    _ = accSM.unpack_value(604, "i")

    # Read the absinaction value
    # Field is not used by ACC
    _ = accSM.unpack_value(608, "i")

    # Read the suspensionDamage value
    suspension_damage_fl = accSM.unpack_value(612, "f")
    suspension_damage_fr = accSM.unpack_value(616, "f")
    suspension_damage_rl = accSM.unpack_value(620, "f")
    suspension_damage_rr = accSM.unpack_value(624, "f")
    suspension_damage = Wheels(
        suspension_damage_fl, suspension_damage_fr, suspension_damage_rl, suspension_damage_rr
    )

    # Read the tyreTemp value
    # Field is not used by ACC
    _ = accSM.unpack_value(628, "f")
    _ = accSM.unpack_value(632, "f")
    _ = accSM.unpack_value(636, "f")
    _ = accSM.unpack_value(640, "f")

    # Read the water temp value
    water_temp = accSM.unpack_value(644, "f")

    # Read the brakePressure value
    brake_pressure_fl = accSM.unpack_value(648, "f")
    brake_pressure_fr = accSM.unpack_value(652, "f")
    brake_pressure_rl = accSM.unpack_value(656, "f")
    brake_pressure_rr = accSM.unpack_value(660, "f")
    brake_pressure = Wheels(
        brake_pressure_fl, brake_pressure_fr, brake_pressure_rl, brake_pressure_rr
    )

    # Read the frontBrakeCompound value
    front_brake_compound = accSM.unpack_value(664, "i")

    # Read the rearBrakeCompound value
    rear_brake_compound = accSM.unpack_value(668, "i")

    # Read the padLife value
    pad_life_fl = accSM.unpack_value(672, "f")
    pad_life_fr = accSM.unpack_value(676, "f")
    pad_life_rl = accSM.unpack_value(680, "f")
    pad_life_rr = accSM.unpack_value(684, "f")
    pad_life = Wheels(pad_life_fl, pad_life_fr, pad_life_rl, pad_life_rr)

    # Read the discLife value
    disc_life_fl = accSM.unpack_value(688, "f")
    disc_life_fr = accSM.unpack_value(692, "f")
    disc_life_rl = accSM.unpack_value(696, "f")
    disc_life_rr = accSM.unpack_value(700, "f")
    disc_life = Wheels(disc_life_fl, disc_life_fr, disc_life_rl, disc_life_rr)

    # Read the ignitionOn value
    ignition_on = accSM.unpack_value(704, "i") == 1

    # Read the starterEngineOn value
    starter_engine_on = accSM.unpack_value(708, "i") == 1

    # Read the isEngineRunning value
    is_engine_running = accSM.unpack_value(712, "i") == 1

    # Read the kerbVibration value
    kerb_vibration = accSM.unpack_value(716, "f")

    # Read the slipVibrations value
    slip_vibration = accSM.unpack_value(720, "f")

    # Read the gVibrations value
    g_vibration = accSM.unpack_value(724, "f")

    # Read the absVibrations value
    abs_vibration = accSM.unpack_value(728, "f")

    return PhysicsMap(
        packed_id=packed_id,
        gas=gas,
        brake=brake,
        fuel=fuel,
        gear=gear,
        rpm=rpm,
        steer_angle=steer_angle,
        speed_kmh=speed_kmh,
        velocity=velocity,
        g_force=g_force,
        wheel_slip=wheel_slip,
        wheel_pressure=wheel_pressure,
        wheel_angular_s=wheel_angular_speed,
        tyre_core_temp=tyre_core_temp,
        suspension_travel=suspension_travel,
        tc=tc,
        heading=heading,
        pitch=pitch,
        roll=roll,
        car_damage=car_damage,
        pit_limiter_on=pit_limiter_on,
        abs=abs_value,
        autoshifter_on=autoshifter_on,
        turbo_boost=turbo_boost,
        air_temp=air_temp,
        road_temp=road_temp,
        local_angular_vel=local_angular_vel,
        final_ff=final_ff,
        brake_temp=brake_temp,
        clutch=clutch,
        is_ai_controlled=is_ai_controlled,
        tyre_contact_point=tyre_contact_point,
        tyre_contact_normal=tyre_contact_normal,
        tyre_contact_heading=tyre_contact_heading,
        brake_bias=brake_bias,
        local_velocity=local_velocity,
        slip_ratio=slip_ratio,
        slip_angle=slip_angle,
        suspension_damage=suspension_damage,
        water_temp=water_temp,
        brake_pressure=brake_pressure,
        front_brake_compound=front_brake_compound,
        rear_brake_compound=rear_brake_compound,
        pad_life=pad_life,
        disc_life=disc_life,
        ignition_on=ignition_on,
        starter_engine_on=starter_engine_on,
        is_engine_running=is_engine_running,
        kerb_vibration=kerb_vibration,
        slip_vibration=slip_vibration,
        g_vibration=g_vibration,
        abs_vibration=abs_vibration,
    )


def read_graphics_map(accSM: accSM) -> GraphicsMap:
    """
    Read the graphics map from the shared memory.

    Parameters:
    accSM: accSM
        The shared memory object.

    Return:
    result: GraphicsMap
        The graphics map.
    """

    # Read the packed ID
    packed_id = accSM.unpack_value(0, "i")

    # Read the status value
    status_value = accSM.unpack_value(4, "i")
    status = ACC_STATUS(status_value)

    # Read the session type value
    session_type_value = accSM.unpack_value(8, "i")
    session_type = ACC_SESSION_TYPE(session_type_value)

    # Read the current time value
    current_time_str = accSM.unpack_string(12, 15)

    # Read the last time value
    last_time_str = accSM.unpack_string(27, 15)

    # Read the best time value
    best_time_str = accSM.unpack_string(42, 15)

    # Read the last sector time value
    last_sector_time_str = accSM.unpack_string(57, 15)

    # Read the completed lap value
    completed_lap = accSM.unpack_value(72, "i")

    # Read the position value
    position = accSM.unpack_value(76, "i")

    # Read the current time value
    current_time = accSM.unpack_value(80, "i")

    # Read the last time value
    last_time = accSM.unpack_value(84, "i")

    # Read the best time value
    best_time = accSM.unpack_value(88, "i")

    # Read the session time left value
    session_time_left = accSM.unpack_value(92, "f")

    # Read the distance traveled value
    distance_traveled = accSM.unpack_value(96, "f")

    # Read the is in pit value
    is_in_pit = accSM.unpack_value(100, "i") == 1

    # Read the current sector index value
    current_sector_index = accSM.unpack_value(104, "i")

    # Read the last sector time value
    last_sector_time = accSM.unpack_value(108, "i")

    # Read the number of laps value
    number_of_laps = accSM.unpack_value(112, "i")

    # Read the tyre compound value
    tyre_compound = accSM.unpack_string(116, 33)

    # Read the normalized car position value
    normalized_car_position = accSM.unpack_value(152, "f")

    # Read the active cars value
    active_cars = accSM.unpack_value(156, "i")

    # Read the car coordinates value
    car_coordinates = []
    for i in range(60):
        car_coordinates_x = accSM.unpack_value(160 + i * 12, "f")
        car_coordinates_y = accSM.unpack_value(164 + i * 12, "f")
        car_coordinates_z = accSM.unpack_value(168 + i * 12, "f")
        car_coordinates.append(Vector3f(car_coordinates_x, car_coordinates_y, car_coordinates_z))

    # Read the car id value
    car_id = accSM.unpack_array(880, "i", 60)

    # Read the player car id value
    player_car_id = accSM.unpack_value(1120, "i")

    # Read the penalty time value
    penalty_time = accSM.unpack_value(1124, "f")

    # Read the flag value
    flag_value = accSM.unpack_value(1128, "i")
    flag = ACC_FLAG_TYPE(flag_value)

    # Read the penalty value
    penalty_value = accSM.unpack_value(1132, "i")
    try:
        penalty = ACC_PENALTY_TYPE(penalty_value)
    except ValueError:
        penalty = ACC_PENALTY_TYPE.UnknownValue

    # Read the ideal line on value
    ideal_line_on = accSM.unpack_value(1136, "i") == 1

    # Read the is in pit lane value
    is_in_pit_lane = accSM.unpack_value(1140, "i") == 1

    # Read the mandatory pit done value
    mandatory_pit_done = accSM.unpack_value(1144, "i") == 1

    # Read the wind speed value
    wind_speed = accSM.unpack_value(1148, "f")

    # Read the wind direction value
    wind_direction = accSM.unpack_value(1152, "f")

    # Read the is setup menu visible value
    is_setup_menu_visible = accSM.unpack_value(1156, "i") == 1

    # Read the main display index value
    main_display_index = accSM.unpack_value(1160, "i")

    # Read the secondary display index value
    secondary_display_index = accSM.unpack_value(1164, "i")

    # Read the TC level value
    tc_level = accSM.unpack_value(1168, "i")

    # Read the TC cut level value
    tc_cut_level = accSM.unpack_value(1172, "i")

    # Read the engine map value
    engine_map = accSM.unpack_value(1176, "i")

    # Read the ABS level value
    abs_level = accSM.unpack_value(1180, "i")

    # Read the fuel per lap value
    fuel_per_lap = accSM.unpack_value(1184, "f")

    # Read the rain light value
    rain_light = accSM.unpack_value(1188, "i") == 1

    # Read the flashing light value
    flashing_light = accSM.unpack_value(1192, "i") == 1

    # Read the light stage value
    light_stage = accSM.unpack_value(1196, "i")

    # Read the exhaust temp value
    exhaust_temp = accSM.unpack_value(1200, "f")

    # Read the wiper stage value
    wiper_stage = accSM.unpack_value(1204, "i")

    # Read the driver stint total time left value
    driver_stint_total_time_left = accSM.unpack_value(1208, "i")

    # Read the driver stint time left value
    driver_stint_time_left = accSM.unpack_value(1212, "i")

    # Read the rain tyres value
    rain_tyres = accSM.unpack_value(1216, "i") == 1

    # Read the session index value
    session_index = accSM.unpack_value(1220, "i")

    # Read the used fuel value
    used_fuel = accSM.unpack_value(1224, "f")

    # Read the delta lap time value
    delta_lap_time_str = accSM.unpack_string(1228, 15)

    # Read the delta lap time value
    delta_lap_time = accSM.unpack_value(1244, "i")

    # Read the estimated lap time value
    estimated_lap_time_str = accSM.unpack_string(1248, 15)

    # Read the estimated lap time value
    estimated_lap_time = accSM.unpack_value(1264, "i")

    # Read the is delta positive value
    is_delta_positive = accSM.unpack_value(1268, "i") == 1

    # Read the is valid lap value
    is_valid_lap = accSM.unpack_value(1272, "i") == 1

    # Read the fuel estimated laps value
    fuel_estimated_laps = accSM.unpack_value(1276, "f")

    # Read the track status value
    track_status = accSM.unpack_string(1280, 33)

    # Read the missing mandatory pits value
    missing_mandatory_pits = accSM.unpack_value(1316, "i")

    # Read the clock value
    clock = accSM.unpack_value(1320, "f")

    # Read the direction light left value
    direction_light_left = accSM.unpack_value(1324, "i") == 1

    # Read the direction light right value
    direction_light_right = accSM.unpack_value(1328, "i") == 1

    # Read the global yellow value
    global_yellow = accSM.unpack_value(1332, "i") == 1

    # Read the global yellow S1 value
    global_yellow_s1 = accSM.unpack_value(1336, "i") == 1

    # Read the global yellow S2 value
    global_yellow_s2 = accSM.unpack_value(1340, "i") == 1

    # Read the global yellow S3 value
    global_yellow_s3 = accSM.unpack_value(1344, "i") == 1

    # Read the global white value
    global_white = accSM.unpack_value(1348, "i") == 1

    # Read the global green value
    global_green = accSM.unpack_value(1352, "i") == 1

    # Read the global chequered value
    global_chequered = accSM.unpack_value(1356, "i") == 1

    # Read the global red value
    global_red = accSM.unpack_value(1360, "i") == 1

    # Read the mfd tyre set value
    mfd_tyre_set = accSM.unpack_value(1364, "i")

    # Read the mfd fuel to add value
    mfd_fuel_to_add = accSM.unpack_value(1368, "f")

    # Read the mfd tyre pressure value
    mfd_tyre_pressure_fl = accSM.unpack_value(1372, "f")
    mfd_tyre_pressure_fr = accSM.unpack_value(1376, "f")
    mfd_tyre_pressure_rl = accSM.unpack_value(1380, "f")
    mfd_tyre_pressure_rr = accSM.unpack_value(1384, "f")
    mfd_tyre_pressure = Wheels(
        mfd_tyre_pressure_fl,
        mfd_tyre_pressure_fr,
        mfd_tyre_pressure_rl,
        mfd_tyre_pressure_rr,
    )

    # Read the track grip status value
    track_grip_status_value = accSM.unpack_value(1388, "i")
    track_grip_status = ACC_TRACK_GRIP_STATUS(track_grip_status_value)

    # Read the rain intensity value
    rain_intensity_value = accSM.unpack_value(1392, "i")
    rain_intensity = ACC_RAIN_INTENSITY(rain_intensity_value)

    # Read the rain intensity in 10min value
    rain_intensity_in_10min_value = accSM.unpack_value(1396, "i")
    rain_intensity_in_10min = ACC_RAIN_INTENSITY(rain_intensity_in_10min_value)

    # Read the rain intensity in 30min value
    rain_intensity_in_30min_value = accSM.unpack_value(1400, "i")
    rain_intensity_in_30min = ACC_RAIN_INTENSITY(rain_intensity_in_30min_value)

    # Read the current tyre set value
    current_tyre_set = accSM.unpack_value(1404, "i")

    # Read the strategy tyre set value
    strategy_tyre_set = accSM.unpack_value(1408, "i")

    # Read the gap ahead value
    gap_ahead = accSM.unpack_value(1412, "i")

    # Read the gap behind value
    gap_behind = accSM.unpack_value(1416, "i")

    return GraphicsMap(
        packed_id=packed_id,
        status=status,
        session_type=session_type,
        current_time_str=current_time_str,
        last_time_str=last_time_str,
        best_time_str=best_time_str,
        last_sector_time_str=last_sector_time_str,
        completed_lap=completed_lap,
        position=position,
        current_time=current_time,
        last_time=last_time,
        best_time=best_time,
        session_time_left=session_time_left,
        distance_traveled=distance_traveled,
        is_in_pit=is_in_pit,
        current_sector_index=current_sector_index,
        last_sector_time=last_sector_time,
        number_of_laps=number_of_laps,
        tyre_compound=tyre_compound,
        normalized_car_position=normalized_car_position,
        active_cars=active_cars,
        car_coordinates=car_coordinates,
        car_id=car_id,
        player_car_id=player_car_id,
        penalty_time=penalty_time,
        flag=flag,
        penalty=penalty,
        ideal_line_on=ideal_line_on,
        is_in_pit_lane=is_in_pit_lane,
        mandatory_pit_done=mandatory_pit_done,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        is_setup_menu_visible=is_setup_menu_visible,
        main_display_index=main_display_index,
        secondary_display_index=secondary_display_index,
        tc_level=tc_level,
        tc_cut_level=tc_cut_level,
        engine_map=engine_map,
        abs_level=abs_level,
        fuel_per_lap=fuel_per_lap,
        rain_light=rain_light,
        flashing_light=flashing_light,
        light_stage=light_stage,
        exhaust_temp=exhaust_temp,
        wiper_stage=wiper_stage,
        driver_stint_total_time_left=driver_stint_total_time_left,
        driver_stint_time_left=driver_stint_time_left,
        rain_tyres=rain_tyres,
        session_index=session_index,
        used_fuel=used_fuel,
        delta_lap_time_str=delta_lap_time_str,
        delta_lap_time=delta_lap_time,
        estimated_lap_time_str=estimated_lap_time_str,
        estimated_lap_time=estimated_lap_time,
        is_delta_positive=is_delta_positive,
        is_valid_lap=is_valid_lap,
        fuel_estimated_laps=fuel_estimated_laps,
        track_status=track_status,
        missing_mandatory_pits=missing_mandatory_pits,
        clock=clock,
        direction_light_left=direction_light_left,
        direction_light_right=direction_light_right,
        global_yellow=global_yellow,
        global_yellow_s1=global_yellow_s1,
        global_yellow_s2=global_yellow_s2,
        global_yellow_s3=global_yellow_s3,
        global_white=global_white,
        global_green=global_green,
        global_chequered=global_chequered,
        global_red=global_red,
        mfd_tyre_set=mfd_tyre_set,
        mfd_fuel_to_add=mfd_fuel_to_add,
        mfd_tyre_pressure=mfd_tyre_pressure,
        track_grip_status=track_grip_status,
        rain_intensity=rain_intensity,
        rain_intensity_in_10min=rain_intensity_in_10min,
        rain_intensity_in_30min=rain_intensity_in_30min,
        current_tyre_set=current_tyre_set,
        strategy_tyre_set=strategy_tyre_set,
        gap_ahead=gap_ahead,
        gap_behind=gap_behind,
    )


def read_static_map(accSM: accSM) -> StaticsMap:
    """
    Read the static map from the shared memory.

    Parameters:
    accSM: accSM
        The shared memory object.

    Return:
    result: StaticsMap
        The static map.
    """

    # Read the sm version value
    sm_version = accSM.unpack_string(0, 15)

    # Read the ac version value
    ac_version = accSM.unpack_string(15, 15)

    # Read the number of session value
    number_of_session = accSM.unpack_value(30, "i")

    # Read the num cars value
    num_cars = accSM.unpack_value(34, "i")

    # Read the car model value
    car_model = accSM.unpack_string(38, 33)

    # Read the track value
    track = accSM.unpack_string(71, 33)

    # Read the player name value
    player_name = accSM.unpack_string(104, 33)

    # Read the player surname value
    player_surname = accSM.unpack_string(137, 33)

    # Read the player nick value
    player_nick = accSM.unpack_string(170, 33)

    # Read the sector count value
    sector_count = accSM.unpack_value(204, "i")

    # Read the max rpm value
    max_rpm = accSM.unpack_value(208, "i")

    # Read the max fuel value
    max_fuel = accSM.unpack_value(212, "f")

    # Read the penalty enabled value
    penalty_enabled = accSM.unpack_value(216, "i") == 1

    # Read the aid fuel rate value
    aid_fuel_rate = accSM.unpack_value(220, "f")

    # Read the aid tyre rate value
    aid_tyre_rate = accSM.unpack_value(224, "f")

    # Read the aid mechanical damage value
    aid_mechanical_damage = accSM.unpack_value(228, "f")

    # Read the aid stability value
    aid_stability = accSM.unpack_value(232, "f")

    # Read the aid auto clutch value
    aid_auto_clutch = accSM.unpack_value(236, "i") == 1

    # Read the pit window start value
    pit_window_start = accSM.unpack_value(240, "i")

    # Read the pit window end value
    pit_window_end = accSM.unpack_value(244, "i")

    # Read the is online value
    is_online = accSM.unpack_value(248, "i") == 1

    # Read the dry tyres name value
    dry_tyres_name = accSM.unpack_string(252, 33)

    # Read the wet tyres name value
    wet_tyres_name = accSM.unpack_string(285, 33)

    return StaticsMap(
        sm_version=sm_version,
        ac_version=ac_version,
        number_of_session=number_of_session,
        num_cars=num_cars,
        car_model=car_model,
        track=track,
        player_name=player_name,
        player_surname=player_surname,
        player_nick=player_nick,
        sector_count=sector_count,
        max_rpm=max_rpm,
        max_fuel=max_fuel,
        penalty_enabled=penalty_enabled,
        aid_fuel_rate=aid_fuel_rate,
        aid_tyre_rate=aid_tyre_rate,
        aid_mechanical_damage=aid_mechanical_damage,
        aid_stability=aid_stability,
        aid_auto_clutch=aid_auto_clutch,
        pit_window_start=pit_window_start,
        pit_window_end=pit_window_end,
        is_online=is_online,
        dry_tyres_name=dry_tyres_name,
        wet_tyres_name=wet_tyres_name,
    )


def penalty_workarround(penalty_value: int) -> ACC_PENALTY_TYPE:
    """
    Workaround for penalty type.

    Parameters:
    penalty_value: int
        The penalty value.

    Return:
    result: ACC_PENALTY_TYPE
        The penalty type.
    """

    try:
        return ACC_PENALTY_TYPE(penalty_value)
    except ValueError:
        return ACC_PENALTY_TYPE.UnknownValue


class accSharedMemory:
    """
    Class to read the shared memory from Assetto Corsa Competizione.
    """

    def __init__(self) -> None:
        """
        Initialize the shared memory.
        """

        self.physics_sm: Optional[accSM] = None
        self.graphics_sm: Optional[accSM] = None
        self.static_sm: Optional[accSM] = None

    def read_shared_memory(self) -> ACC_map:
        """
        Read the shared memory.

        Return:
        result: ACC_map
            The shared memory data.
        """

        if self.physics_sm is None:
            self.physics_sm = accSM(
                -1, 732, tagname="Local\\acpmf_physics", access=mmap.ACCESS_READ
            )

        if self.graphics_sm is None:
            self.graphics_sm = accSM(
                -1, 1420, tagname="Local\\acpmf_graphics", access=mmap.ACCESS_READ
            )

        if self.static_sm is None:
            self.static_sm = accSM(
                -1, 318, tagname="Local\\acpmf_static", access=mmap.ACCESS_READ
            )

        physics = read_physic_map(self.physics_sm)
        graphics = read_graphics_map(self.graphics_sm)
        static = read_static_map(self.static_sm)

        return ACC_map(Physics=physics, Graphics=graphics, Static=static)

    def get_shared_memory_data(self) -> ACC_map:
        """
        Get the shared memory data.

        Return:
        result: ACC_map
            The shared memory data.
        """

        try:
            return self.read_shared_memory()
        except Exception as e:
            raise SharedMemoryTimeout(f"Error reading shared memory: {e}")

    def close(self) -> None:
        """
        Close the shared memory.
        """

        if self.physics_sm is not None:
            self.physics_sm.close()
            self.physics_sm = None

        if self.graphics_sm is not None:
            self.graphics_sm.close()
            self.graphics_sm = None

        if self.static_sm is not None:
            self.static_sm.close()
            self.static_sm = None


def simple_test() -> None:
    """
    Simple test to read the shared memory.
    """

    import time

    sm = accSharedMemory()

    try:
        while True:
            data = sm.get_shared_memory_data()
            print(f"Status: {data.Graphics.status}")
            print(f"Session Type: {data.Graphics.session_type}")
            print(f"RPM: {data.Physics.rpm}")
            print(f"Speed: {data.Physics.speed_kmh} km/h")
            print(f"Gear: {data.Physics.gear}")
            print(f"Fuel: {data.Physics.fuel} L")
            print(f"Tyre Pressure: {data.Physics.wheel_pressure}")
            print(f"Tyre Core Temp: {data.Physics.tyre_core_temp}")
            print(f"Brake Temp: {data.Physics.brake_temp}")
            print(f"Brake Pressure: {data.Physics.brake_pressure}")
            print(f"TC: {data.Physics.tc}")
            print(f"ABS: {data.Physics.abs}")
            print(f"Car Damage: {data.Physics.car_damage}")
            print(f"Suspension Travel: {data.Physics.suspension_travel}")
            print(f"Suspension Damage: {data.Physics.suspension_damage}")
            print(f"Water Temp: {data.Physics.water_temp}")
            print(f"Brake Bias: {data.Physics.brake_bias}")
            print(f"Slip Ratio: {data.Physics.slip_ratio}")
            print(f"Slip Angle: {data.Physics.slip_angle}")
            print(f"Pad Life: {data.Physics.pad_life}")
            print(f"Disc Life: {data.Physics.disc_life}")
            print(f"Track: {data.Static.track}")
            print(f"Car Model: {data.Static.car_model}")
            print(f"Player Name: {data.Static.player_name}")
            print(f"Player Surname: {data.Static.player_surname}")
            print(f"Player Nick: {data.Static.player_nick}")
            print(f"Max RPM: {data.Static.max_rpm}")
            print(f"Max Fuel: {data.Static.max_fuel}")
            print(f"Penalty Enabled: {data.Static.penalty_enabled}")
            print(f"Aid Fuel Rate: {data.Static.aid_fuel_rate}")
            print(f"Aid Tyre Rate: {data.Static.aid_tyre_rate}")
            print(f"Aid Mechanical Damage: {data.Static.aid_mechanical_damage}")
            print(f"Aid Stability: {data.Static.aid_stability}")
            print(f"Aid Auto Clutch: {data.Static.aid_auto_clutch}")
            print(f"Pit Window Start: {data.Static.pit_window_start}")
            print(f"Pit Window End: {data.Static.pit_window_end}")
            print(f"Is Online: {data.Static.is_online}")
            print(f"Dry Tyres Name: {data.Static.dry_tyres_name}")
            print(f"Wet Tyres Name: {data.Static.wet_tyres_name}")
            print("\n")
            time.sleep(1)
    except KeyboardInterrupt:
        sm.close()
        print("Closed shared memory.")


if __name__ == "__main__":
    simple_test()