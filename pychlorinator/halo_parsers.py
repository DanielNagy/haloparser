"""protocol parsers and types for halo chlorinator API"""

import struct

from enum import Enum, IntFlag, IntEnum

class ScanResponse:
    _fmt = '<BBBBBBI4sBBBBBBB'
    def __init__(self, data) -> None:
        fields = struct.unpack(self._fmt, data[: struct.calcsize(self._fmt)])
        (
            # self.ManufacturerIdLo,
            # self.ManufacturerIdHi,
            self.DeviceType,
            self.DeviceVersion,
            self.DeviceProtocol,
            self.DeviceProtocolRevision,
            self.DeviceStatus,
            self._reserved,
            self.DeviceUniqueId, # 4 bytes
            self.ByteAccessCode, # 4 bytes
            self.FirmwareMajorVersion,
            self.FirmwareMinorVersion,
            self.BootloaderMajorVersion,
            self.BootloaderMinorVersion,
            self.HardwarePlatformIdLo,
            self.HardwarePlatformIdHi,
            self.TimeAlive,
        ) = fields

        self.isPairable = self.ByteAccessCode != b'\x00\x00\x00\x00'
        self.DeviceType = DeviceType(self.DeviceType)
        self.DeviceProtocol = DeviceProtocol(self.DeviceProtocol)

class DeviceProfileCharacteristic2:
    def __init__(self, data, fmt='<BBBBBBBBBI'):
        (
            self.DeviceType,
            self.DeviceVersion,
            self.DeviceProtocol,
            self.DeviceProtocolRevision,
            self.FirmwareVersionMajor,
            self.FirmwareVersionMinor,
            self.BootloaderVersionMajor,
            self.BootloaderVersionMinor,
            self.HardwareVersion,
            self.SerialNumber,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])

        self.DeviceType = DeviceType(self.DeviceType)
        self.DeviceProtocol = DeviceProtocol(self.DeviceProtocol)

class TempCharacteristic:
    
    fmt = "<BBHHHHBHHB"
    def __init__(self, data):
        (
            self.IsFahrenheit,
            self.TempSupports,
            self.BoardTemp,
            self.WaterTemp,
            self.ChloroWater,
            self.SolarWater,
            self.WaterTempValid,
            self.SolarRoof,
            self.Heater,
            self.TempDisplayed,
        ) = struct.unpack(self.fmt, data[: struct.calcsize(self.fmt)])

        self.BoardTemp /= 10 # assumption Not in .net code???
        self.WaterTemp /= 10
        self.ChloroWater /= 10 # assumption as not in .net code???
        self.SolarWater /= 10 # assumption as not in .net code???
        self.SolarRoof /= 10 # assumption as not in .net code???
        self.Heater /= 10  # assumption as not in .net code???

        self.TempSupports = self.temp_supports_flags
        self.TempDisplayed = self.temp_displayed_flags

    @property
    def temp_supports_flags(self):
        return self.TempSupportsValues(self.TempSupports)

    @property
    def temp_displayed_flags(self):
        return self.TempDisplayedValues(self.TempDisplayed)

    
    class TempSupportsValues(IntFlag):
        BoardTemp = 1
        WaterTemp = 2
        ChloroWater = 4
        SolarWater = 8
        SolarRoof = 16
        Heater = 32


    class TempDisplayedValues(IntFlag):
        BoardTemp = 1
        WaterTemp = 2
        ChloroWater = 4
        SolarWater = 8
        SolarRoof = 16
        Heater = 32

class SettingsCharacteristic2:
    fmt = "<HBBBBBB"
    def __init__(self, data):
        (
            self.General,
            self.CellModel,
            self.ReversalPeriod,
            self.AIWaterTurns,
            self.AcidPumpSize,
            self.FilterPumpSize,
            self.DefaultManualOnSpeed,
        ) = struct.unpack(self.fmt, data[: struct.calcsize(self.fmt)])

        self.General = self.general_values
        self.CellModel = self.CellModelValues(self.CellModel)

    @property
    def general_values(self):
        return self.GeneralValues(self.General)

    class GeneralValues(IntFlag):
        PrePurgeEnabled = 1
        PostPurgeEnabled = 2
        AcidFlushEnabled = 4
        AIEnabled = 8
        AIEnabledReadOnly = 16
        DisplayORP = 32
        DosingEnabled = 64
        ThreeSpeedPumpEnabled = 128
        ThreeSpeedPumpEnabledReadOnly = 256
        PumpProtectEnable = 512
        UseTemperatureSensor = 1024
        EnableCleaningInterlock = 2048
        DisplayPH = 4096

    class CellModelValues(IntEnum):
        Model_18 = 0
        Model_25 = 1
        Model_35 = 2
        Model_45 = 3

class StateCharacteristic3:
    fmt = "<BBHBBHBBB2sHB"
    
    def __init__(self, data):
        (
            self.Flags,
            self.RealCelllevel,
            self.CellCurrentmA,
            self.MainText,
            self.SubText1Chlorine,
            self.ORPMeasurement,
            self.SubText2Ph,
            self.PHMeasurement,
            self.SubText3TimerInfo,
            *self.SubText3BytesData,
            self.SubText4ErrorInfo,
            self.Flag,
        ) = struct.unpack(self.fmt, data[: struct.calcsize(self.fmt)])

        self.Flags = self.flags_values
        self.PHMeasurement /= 10


    @property
    def flags_values(self):
        return self.FlagsValues(self.Flags)

    class FlagsValues(IntFlag):
        SpaMode = 1
        CellOn = 2
        CellReversed = 4
        CoolingFanOn = 8
        LightOutputOn = 16
        DosingPumpOn = 32
        CellIsReversing = 64
        AIModeActive = 128


class WaterVolumeCharacteristic:
    def __init__(self, data, fmt='<BIHIHB'):
        (
            self.VolumeUnits,
            self.PoolVolume,
            self.SpaVolume,
            self.PoolLeftFilter,
            self.SpaLeftFilter,
            self.Flag,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])
        self.Flag = self.flag_values
        self.VolumeUnits = self.VolumeUnit_value
        
    @property
    def flag_values(self):
        return self.FlagValues(self.Flag)
    
    @property
    def VolumeUnit_value(self):
        return self.VolumeUnitsValues(self.VolumeUnits)

    class FlagValues(IntFlag):
        PoolEnabled = 1
        SpaEnabled = 2

    class VolumeUnitsValues(Enum):
        Litres = 0
        UsGallons = 1
        ImperialGallons = 2


class SetPointCharacteristic:
    def __init__(self, data, fmt='<BHBBB'):
        (
            self.PhControlSetpoint,
            self.OrpControlSetpoint,
            self.PoolChlorineControlSetpoint,
            self.AcidControlSetpoint,
            self.SpaChlorineControlSetpoint,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])


        self.PhControlSetpoint /= 10

        

class CapabilitiesCharacteristic2:
    def __init__(self, data, fmt='<BB'):
        (
            self.PhControlType,
            self.OrpControlType,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])
        
        # Minimum setpoints
        self.MinimumManualAcidSetpoint = 0
        self.MinimumManualChlorineSetpoint = 0
        self.MinimumOrpSetpoint = 100
        self.MinimumPhSetpoint = 3.0

        # Maximum setpoints
        self.MaximumManualAcidSetpoint = 10
        self.MaximumManualChlorineSetpoint = 8
        self.MaximumOrpSetpoint = 800
        self.MaximumPhSetpoint = 10.0

        self.PhControlType = self.PhControlType_value
        self.ChlorineControlType = self.ChlorineControlType_value

    @property
    def PhControlType_value(self):
        return self.PhControlTypes(self.PhControlType)

    @property
    def ChlorineControlType_value(self):
        return self.ChlorineControlTypes(self.OrpControlType)

    class PhControlTypes(Enum):
        NoneType = 0
        Manual = 1
        Automatic = 2
    class ChlorineControlTypes(Enum):
        NoneType = 0
        Manual = 1
        Automatic = 2


class EquipmentModeCharacteristic:
    def __init__(self, data, fmt='<BBBBBBBBBBBBHH'):
        (
            self.EquipmentEnabled,
            self.FilterPumpMode,
            self.ModeGPO1,
            self.ModeGPO2,
            self.ModeGPO3,
            self.ModeGPO4,
            self.ModeValve1,
            self.ModeValve2,
            self.ModeValve3,
            self.ModeValve4,
            self.ModeRelay1,
            self.ModeRelay2,
            self.StateBitfield,
            self.AutoEnabledBitfield,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])

        self.EquipmentEnabled == 1 # is this correct?
        self.FilterPumpMode = Mode(self.FilterPumpMode)
        self.FilterPumpState = bool(self.StateBitfieldValues.FilterPump & self.StateBitfield)
        self.AutoEnabledFilterPump = bool(self.AutoEnabledBitfieldValues.FilterPump & self.AutoEnabledBitfield)

        self.GPO1_Mode = GPOMode(self.ModeGPO1)
        self.GPO1_State = bool(self.StateBitfieldValues.GPO1 & self.StateBitfield)
        self.GPO1_AutoEnabled = bool(self.StateBitfieldValues.GPO1 & self.AutoEnabledBitfield)
        self.GPO2_Mode = GPOMode(self.ModeGPO2)
        self.GPO2_State = bool(self.StateBitfieldValues.GPO2 & self.StateBitfield)
        self.GPO2_AutoEnabled = bool(self.StateBitfieldValues.GPO2 & self.AutoEnabledBitfield)
        self.GPO3_Mode = GPOMode(self.ModeGPO3)
        self.GPO3_State = bool(self.StateBitfieldValues.GPO3 & self.StateBitfield)
        self.GPO3_AutoEnabled = bool(self.StateBitfieldValues.GPO3 & self.AutoEnabledBitfield)
        self.GPO4_Mode = GPOMode(self.ModeGPO4)
        self.GPO4_State = bool(self.StateBitfieldValues.GPO4 & self.StateBitfield)
        self.GPO4_AutoEnabled = bool(self.StateBitfieldValues.GPO4 & self.AutoEnabledBitfield)

        self.Valve1_Mode = GPOMode(self.ModeValve1)
        self.Valve1_State = bool(self.StateBitfieldValues.Valve1 & self.StateBitfield)
        self.Valve1_AutoEnabled = bool(self.StateBitfieldValues.Valve1 & self.AutoEnabledBitfield)
        self.Valve2_Mode = GPOMode(self.ModeValve2)
        self.Valve2_State = bool(self.StateBitfieldValues.Valve2 & self.StateBitfield)
        self.Valve2_AutoEnabled = bool(self.StateBitfieldValues.Valve2 & self.AutoEnabledBitfield)
        self.Valve3_Mode = GPOMode(self.ModeValve3)
        self.Valve3_State = bool(self.StateBitfieldValues.Valve3 & self.StateBitfield)
        self.Valve3_AutoEnabled = bool(self.StateBitfieldValues.Valve3 & self.AutoEnabledBitfield)
        self.Valve4_Mode = GPOMode(self.ModeValve4)
        self.Valve4_State = bool(self.StateBitfieldValues.Valve4 & self.StateBitfield)
        self.Valve4_AutoEnabled = bool(self.StateBitfieldValues.Valve4 & self.AutoEnabledBitfield)

        self.Relay1_Mode = GPOMode(self.ModeRelay1)
        self.Relay1_State = bool(self.StateBitfieldValues.Relay1 & self.StateBitfield)
        self.Relay1_AutoEnabled = bool(self.StateBitfieldValues.Relay1 & self.AutoEnabledBitfield)
        self.Relay2_Mode = GPOMode(self.ModeRelay2)
        self.Relay2_State = bool(self.StateBitfieldValues.Relay2 & self.StateBitfield)
        self.Relay2_AutoEnabled = bool(self.StateBitfieldValues.Relay2 & self.AutoEnabledBitfield)        

    @property
    def state_bitfield_values(self):
        return self.StateBitfieldValues(self.StateBitfield)

    @property
    def test_value_for_flag(self, value, flag_enum):
        return flag_enum.value & value != 0


    class StateBitfieldValues(IntFlag):
        FilterPump = 1
        GPO1 = 2
        GPO2 = 4
        GPO3 = 8
        GPO4 = 16
        Valve1 = 32
        Valve2 = 64
        Valve3 = 128
        Valve4 = 256
        Relay1 = 512
        Relay2 = 1024


    class AutoEnabledBitfieldValues(IntFlag):
        FilterPump = 1
        GPO1 = 2
        GPO2 = 4
        GPO3 = 8
        GPO4 = 16
        Valve1 = 32
        Valve2 = 64
        Valve3 = 128
        Valve4 = 256
        Relay1 = 512
        Relay2 = 1024


class LightStateCharacteristic:
    def __init__(self, data, fmt='<4s4sB'):
        (
            self.ZoneModes,
            self.ZoneColours,
            self.ZoneStateFlags,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])

        self.LightingMode_1 = Mode(self.ZoneModes[0])
        self.LightingMode_2 = Mode(self.ZoneModes[1])
        self.LightingMode_3 = Mode(self.ZoneModes[2])
        self.LightingMode_4 = Mode(self.ZoneModes[3])
        self.LightingState_1 = self.ZoneStateFlagsValues(self.ZoneStateFlags & 0)
        self.LightingState_2 = self.ZoneStateFlagsValues(self.ZoneStateFlags & 1)
        self.LightingState_3 = self.ZoneStateFlagsValues(self.ZoneStateFlags & 2)
        self.LightingState_4 = self.ZoneStateFlagsValues(self.ZoneStateFlags & 3)
        self.LightingColour_1 = self.ZoneColours[0]
        self.LightingColour_2 = self.ZoneColours[1]
        self.LightingColour_3 = self.ZoneColours[2]
        self.LightingColour_4 = self.ZoneColours[3]
        ''' Mapping of colours is located in namespace AstralPoolService.BusinessObjects.Light '''
        ''' Each model brand type of Light has its own colour. Too much logic to map out here '''
        
        


    @property
    def zone_state_flags_values(self):
        return self.ZoneStateFlagsValues(self.ZoneStateFlags)

    class ZoneStateFlagsValues(IntFlag):
        Zone1On = 1
        Zone2On = 2
        Zone3On = 4
        Zone4On = 8



class LightCapabilitiesCharacteristic:
    def __init__(self, data, fmt='<5B'):
        (
            self.LightingEnabled,
            self.OnBoardLightEnabled,
            self.Model,
            self.NumZonesInUse,
            self.ZoneIsMulticolourFlags,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])

        self.ZoneIsMulticolourFlags = self.ZoneIsMulticolourFlagsValues(self.ZoneIsMulticolourFlags)
    @property
    def zone_is_multicolour_flags_values(self):
        return self.ZoneIsMulticolourFlagsValues(self.ZoneIsMulticolourFlags)

    class ZoneIsMulticolourFlagsValues(IntFlag): # There might be a bug in the .net code, as it is 1/2/3/4, not 1/2/4/8
        Zone1IsMulticolour = 1
        Zone2IsMulticolour = 2
        Zone3IsMulticolour = 4
        Zone4IsMulticolour = 8





class LightSetupCharacteristic:
    def __init__(self, data, fmt='<4s'):
        (
            self.ZoneNames,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])

        self.LightingZoneName_1 = self.ZoneNamesValues(self.ZoneNames[0])
        self.LightingZoneName_2 = self.ZoneNamesValues(self.ZoneNames[1])
        self.LightingZoneName_3 = self.ZoneNamesValues(self.ZoneNames[2])
        self.LightingZoneName_4 = self.ZoneNamesValues(self.ZoneNames[3])


    class ZoneNamesValues(IntEnum):
        Pool = 0
        Spa = 1
        PoolAndSpa = 2
        Waterfall1 = 3
        Waterfall2 = 4
        Waterfall3 = 5
        Garden = 6
        Other = 7


class MaintenanceStateCharacteristic:
    def __init__(self, data, fmt='<BHBBIHBB'):
        (
            self.Flags,
            self.DoseDisableTimeMins,
            self.MaintenanceTaskState,
            self.MaintenanceTaskReturnCode,
            self.TaskTimeRemaining,
            self.ValueToDisplay,
            self.CalibrateState,
            self.ModeAfterComplete,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])

        self.AcidDosingDisabled = bool(self.FlagValues.AcidDosingDisabled & self.Flags)
        self.MaintenanceTaskState = self.TaskStatesValues(self.MaintenanceTaskState)
        self.MaintenanceTaskReturnCode = self.TaskReturnCodesValues(self.MaintenanceTaskReturnCode)
        self.CalibrateState = self.CalibrateStatesValues(self.CalibrateState)
        self.ModeAfterComplete = Mode(self.ModeAfterComplete)

    @property
    def flag_values(self):
        return self.FlagValues(self.Flags)


    class FlagValues(IntEnum):
        AcidDosingDisabled = 1
        DayRolledOver = 2

    class TaskStatesValues(IntEnum):
        NoState = -1  # 0xFFFFFFFF
        NoTask = 0
        SanitiseUntilTimer = 1
        FilterForPeriod = 2
        FilterAndCleanForPeriod = 3
        Backwash = 4
        CalibratePH = 5
        CalibrateORP = 6
        PrimeAcid = 7
        DoseAcid = 8
        SanitiseForPeriod = 9
        SanitiseAndCleanForPeriod = 10

    class TaskReturnCodesValues(IntEnum):
        OK = 0
        FailedSetStartConditions = 1
        TaskOverriddenByUser = 2
        FailedSetSystemMode = 3
        TaskAbortedByUser = 4
        TaskComplete = 5
    
    class CalibrateStatesValues(Enum):
        Idle = 0
        ProbeCalStarting = 1
        ConnectToProbe = 2
        ConnectionFailed = 3
        ReadCalValue = 4
        ReadCalValueFailed = 5
        RunningPump = 6
        TakingMeasurement = 7
        MeasurementFailed = 8
        WaitNewCalValue = 9
        TimeOutWaitingCalibration = 10
        WritingCalibrationValue = 11
        CalibrationFailedToWrite = 12
        CalibrationSuccessful = 13
        CalAbort = 14



class HeaterCapabilitiesCharacteristic:
    def __init__(self, data, fmt='<BBBBB'):
        (
            self.HeaterEnabled,
            self.FilterPumpThreeSpeed,
            self.HeaterPumpThreeSpeed,
            self.HeaterPumpInstalled,
            self.HeaterPumpTimerBit,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])


class HeaterConfigCharacteristic:
    def __init__(self, data, fmt='<BB'):
        (
        self.HeaterPumpEnabled, 
        self.HeaterMinPumpSpeed 
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])


        self.HeaterMinPumpSpeed = self.SpeedLevels(self.HeaterMinPumpSpeed)

    class SpeedLevels(IntEnum):
        NotSet = -1
        Low = 0
        Medium = 1
        High = 2
        AI = 3
    


class HeaterStateCharacteristic:
    def __init__(self, data, fmt='<BBBBBBBBBHB'):
        (
            self.HeaterStatusFlag,
            self.HeaterPumpMode,
            self.HeaterMode,
            self.HeaterSetpoint,
            self.HeatPumpMode,
            self.HeaterForced,
            self.HeaterForcedTimeHrs,
            self.HeaterForcedTimeMins,
            self.HeaterWaterTempValid,
            self.HeaterWaterTemp,
            self.HeaterError,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])

        self.HeaterOn = bool(self.HeaterStatusFlagValues.HeaterOn & self.HeaterStatusFlag)
        self.HeaterPressure = bool(self.HeaterStatusFlagValues.Pressure & self.HeaterStatusFlag)
        self.HeaterGasValve = bool(self.HeaterStatusFlagValues.GasValve & self.HeaterStatusFlag)
        self.HeaterFlame = bool(self.HeaterStatusFlagValues.Flame & self.HeaterStatusFlag)
        self.HeaterLockout = bool(self.HeaterStatusFlagValues.Lockout & self.HeaterStatusFlag)
        self.GeneralServiceRequired = bool(self.HeaterStatusFlagValues.GeneralServiceRequired & self.HeaterStatusFlag)
        self.IgnitionServiceRequired = bool(self.HeaterStatusFlagValues.IgnitionServiceRequired & self.HeaterStatusFlag)
        self.CoolingAvailable = bool(self.HeaterStatusFlagValues.CoolingAvailable & self.HeaterStatusFlag)
        self.HeaterPumpMode = Mode(self.HeaterPumpMode)
        self.HeatPumpMode = self.HeatpumpModeValues(self.HeatPumpMode)
        self.HeaterForced = self.HeaterForcedEnum(self.HeaterForced)
        self.HeaterWaterTempValid = self.TempValidEnum(self.HeaterWaterTempValid)
        self.HeaterWaterTemp /= 10




    @property
    def heater_status_flags(self):
        return HeaterStateCharacteristic.HeaterStatusFlagValues(self.HeaterStatusFlag)

    class HeaterStatusFlagValues(IntFlag):
        HeaterOn = 1
        Pressure = 2
        GasValve = 4
        Flame = 8
        Lockout = 16
        GeneralServiceRequired = 32
        IgnitionServiceRequired = 64
        CoolingAvailable = 128

    class HeatpumpModeValues(Enum):
        Cooling = 0
        Heating = 1
        Auto = 2
    
    class HeaterForcedEnum(Enum):
        NotForced = 0
        ForcedOn = 1
        ForcedOff = 2

    class TempValidEnum(Enum):
        Invalid = 0
        IsValid = 1
        WasValid = 2


class EquipmentParameterCharacteristic:
    def __init__(self, data, fmt='BBBBBBBBBBB'):
        (
            self.FilterPumpSpeed,
            self.ParameterGPO1,
            self.ParameterGPO2,
            self.ParameterGPO3,
            self.ParameterGPO4,
            self.ParameterValve1,
            self.ParameterValve2,
            self.ParameterValve3,
            self.ParameterValve4,
            self.ParameterRelay1,
            self.ParameterRelay2,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])
        self.FilterPumpSpeed = self.SpeedLevels(self.FilterPumpSpeed)

    class SpeedLevels(Enum):
        NotSet = -1
        Low = 0
        Medium = 1
        High = 2
        AI = 3

class DeviceType(Enum):
    """ ScanResponse Device Type"""
    Unknown = -1 # 0xFFFFFFFF
    Pump = 0
    Chlorinator = 1
    Doser = 2
    Light = 3
    Probe = 4
    ChlorinatorEmulator = 129 # 0x00000081


class ProbeCharacteristic:
    def __init__(self, data, fmt='<BBHH'):
        (
            self.HighestPhMeasured,
            self.LowestPhMeasured,
            self.HighestOrpMeasured,
            self.LowestOrpMeasured,
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])
        self.HighestPhMeasured /= 10
        self.LowestPhMeasured /= 10



class CellCharacteristic2:
    def __init__(self, data, fmt='<HIIBHH'):
        (
            self.CellReversalCount,
            self.CellRunningTime, # hrs
            self.LowSaltCellRunningTime,
            self.PreviousDaysCellLoad,
            self.DosingPumpSecs, # ml today
            self.FilterPumpMins, # mins today
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])
        #self.CellRunningTime /= 3600 #??  TimeSpan.FromHours
        #self.LowSaltCellRunningTime /= 3600 #??

class PowerBoardCharacteristic:
    def __init__(self, data, fmt='<I'):
        (
        self.PowerBoardRuntime # hrs
        ) = struct.unpack(fmt, data[: struct.calcsize(fmt)])
        #self.PowerBoardRuntime /= 3600 #??

class HeaterCooldownStateCharacteristic:
    def __init__(self, data, fmt='<BBBBHH'):
        (
            self.HeaterCooldownEventOccurredFlag,
            self.HeaterCooldownState,
            self.Ignore,
            self.TargetMode,
            self.RemainingCooldownTime,
            self.TotalHeaterCooldownTime,
        ) = struct.unpack(fmt, data[:struct.calcsize(fmt)])

class SolarCapabilitiesCharacteristic:
    def __init__(self, data, fmt='<B'):
        self.SolarEnabled = struct.unpack(fmt, data[:struct.calcsize(fmt)])[0]

class SolarConfigCharacteristic:
    def __init__(self, data, fmt='<BBBBBBBHB'):
        (
            self.SolarPumpStartHR,
            self.SolarPumpStartMin,
            self.SolarPumpStopHR,
            self.SolarPumpStopMin,
            self.SolarEnableFlush,
            self.SolarFlushTimeHR,
            self.SolarFlushTimeMin,
            self.Differential,
            self.SolarEnableExclPeriod,
        ) = struct.unpack(fmt, data[:struct.calcsize(fmt)])


class SolarStateCharacteristic:
    def __init__(self, data, fmt='<HHHBBBBBHB'):
        (
            self.SolarRoofTemp,
            self.SolarWaterTemp,
            self.SolarTemp,
            self.SolarSeason,
            self.SolarMode,
            self.SolarFlag,
            self.SolarRoofTempValid,
            self.SolarWaterTempValid,
            self.SolarSpecTemp,
            self.SolarMessage,
        ) = struct.unpack(fmt, data[:struct.calcsize(fmt)])

        self.SolarMode = Mode(self.SolarMode)
        self.SolarPumpState = bool(self.SolarFlagValues.SolarPumpState & self.SolarFlag)
        self.SolarFlushActive = bool(self.SolarFlagValues.SolarFlushActive & self.SolarFlag)
        self.SolarRoofTempValid = self.TempValidEnum(self.SolarRoofTempValid)
        self.SolarWaterTempValid = self.TempValidEnum(self.SolarWaterTempValid)
        self.SolarMessage = self.SolarMessageValues(self.SolarMessage)


    class SolarFlagValues(IntFlag):
        SolarPumpState = 1
        SolarFlushActive = 2

    class SolarMessageValues(Enum):
        DisplayNothing = 0
        Standby = 1
        SolarHeatingActive = 2
        SolarFlushActive = 3
        SolarExcPerActive = 4
        SolarSystemflushed = 5
        PumpWillRunFor = 6

    class TempValidEnum(Enum):
        Invalid = 0
        IsValid = 1
        WasValid = 2


class GPOSetupCharacteristic:
    def __init__(self, data, fmt='<BBBBBBB'):
        (
            self.DeviceType,
            self.Index,
            self.OutletEnabled,
            self.GPOFunction,
            self.GPOName,
            self.GPOLightingZone,
            self.UseTimers,
        ) = struct.unpack(fmt, data[:struct.calcsize(fmt)])

        self.DeviceType = self.GPODeviceTypeValues(self.DeviceType)
        self.GPOFunction = self.GPOFunctionValues(self.GPOFunction)
        self.GPOName = self.GPONameValues(self.GPOName)

    class GPODeviceTypeValues(Enum):
        FilterPump = 0
        PHProbe = 1
        OrpProbe = 2
        Heater = 3
        Light1 = 4
        Light2 = 5
        LightFAB = 6
        Connect1 = 7
        Connect2 = 8

    class GPOFunctionValues(Enum):
        Equipment = 0
        Lighting = 1
        Solar = 2
        Heating = 3

    class GPONameValues(Enum):
        NoName = 0
        Other = 1
        CleaningPump = 2
        HeaterPump = 3
        BoosterPump = 4
        WaterfallPump = 5
        FountainPump = 6
        Blower = 7
        Jets = 8

class RelaySetupCharacteristic:
    def __init__(self, data, fmt='<BBBBB'):
        (
            self.Index,
            self.RelayEnabled,
            self.RelayName,
            self.RelayAction,
            self.UseTimers,
        ) = struct.unpack(fmt, data[:struct.calcsize(fmt)])
        self.RelayName = self.RelayNameValue(self.RelayName)

    class RelayNameValue(Enum):
        Relay1 = 0
        Relay2 = 1


class ValveSetupCharacteristic:

    def __init__(self, data, fmt='<BBBB'):
        (
            self.Index,
            self.ValveEnabled,
            self.ValveName,
            self.UseTimers,
        ) = struct.unpack(fmt, data[:struct.calcsize(fmt)])

        # Convert valve name byte to ValveNameValue enum
        self.ValveName = self.ValveNameValue(self.ValveName)

    class ValveNameValue(Enum):
        NoneValue = 0
        Other = 1
        Pool = 2
        Spa = 3
        WaterFeature = 4
        Waterfall = 5



class DeviceProtocol(Enum):
    """ ScanResponse Device Protocol"""
    Unknown = -1
    Protocol0 = 0
    Firmware57 = 1
    NextGen = 2


class Mode(Enum):
    Off = 0
    Auto = 1
    On = 2


class GPOMode(Enum):
    Off = 0
    Auto = 1
    On = 2
    NotEnabled = 255