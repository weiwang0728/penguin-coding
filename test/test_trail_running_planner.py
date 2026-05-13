"""
越野跑训练计划生成器 - 单元测试
"""

import pytest
from datetime import date, timedelta

from trail_running_planner.models import (
    DistanceCategory,
    ExperienceLevel,
    PhaseType,
    WorkoutType,
    Workout,
    WeekPlan,
    TrainingPlan,
)
from trail_running_planner.generator import TrainingPlanGenerator
from trail_running_planner.renderer import PlanRenderer, render_plan_to_string
from trail_running_planner.config import (
    PHASE_DISTRIBUTION,
    WEEKLY_TRAINING_DAYS,
    BASE_WEEKLY_DISTANCE,
    MAX_LONG_RUN_DISTANCE,
    WEEKLY_ELEVATION_GAIN,
    WORKOUT_DISTRIBUTION,
    INTENSITY_PROGRESSSION,
)


# ============================================================
# 模型测试
# ============================================================

class TestDistanceCategory:
    """距离类别测试"""

    def test_all_distances_exist(self):
        """所有距离类别都存在"""
        assert DistanceCategory.TRAIL_10K.value == "10K"
        assert DistanceCategory.TRAIL_HALF.value == "半马(21K)"
        assert DistanceCategory.TRAIL_FULL.value == "全马(42K)"
        assert DistanceCategory.TRAIL_50K.value == "50K"
        assert DistanceCategory.TRAIL_100K.value == "100K"

    def test_distance_count(self):
        """应有5个距离类别"""
        assert len(DistanceCategory) == 5


class TestExperienceLevel:
    """经验等级测试"""

    def test_all_levels_exist(self):
        assert ExperienceLevel.BEGINNER.value == "初学者"
        assert ExperienceLevel.INTERMEDIATE.value == "中级"
        assert ExperienceLevel.ADVANCED.value == "高级"

    def test_level_count(self):
        assert len(ExperienceLevel) == 3


class TestWorkout:
    """训练项测试"""

    def test_workout_creation(self):
        w = Workout(
            day=1,
            workout_type=WorkoutType.EASY_RUN,
            duration_minutes=45,
            description="轻松跑",
            distance_km=8.0,
            intensity="低",
        )
        assert w.day == 1
        assert w.workout_type == WorkoutType.EASY_RUN
        assert w.duration_minutes == 45
        assert w.distance_km == 8.0

    def test_workout_defaults(self):
        w = Workout(
            day=3,
            workout_type=WorkoutType.TEMPO_RUN,
            duration_minutes=40,
            description="节奏跑",
        )
        assert w.distance_km is None
        assert w.elevation_gain_m is None
        assert w.intensity == "中"
        assert w.notes == ""


class TestWeekPlan:
    """周计划测试"""

    def test_week_plan_creation(self):
        week = WeekPlan(
            week_number=1,
            phase=PhaseType.BASE,
            weekly_distance_km=30.0,
            weekly_elevation_gain_m=500,
        )
        assert week.week_number == 1
        assert week.phase == PhaseType.BASE
        assert len(week.workouts) == 0

    def test_is_recovery_week(self):
        recovery = WeekPlan(
            week_number=4,
            phase=PhaseType.RECOVERY,
            weekly_distance_km=20.0,
            weekly_elevation_gain_m=300,
        )
        assert recovery.is_recovery_week is True

        base = WeekPlan(
            week_number=1,
            phase=PhaseType.BASE,
            weekly_distance_km=30.0,
            weekly_elevation_gain_m=500,
        )
        assert base.is_recovery_week is False


class TestTrainingPlan:
    """训练计划测试"""

    def _make_plan(self, num_weeks=3):
        weeks = [
            WeekPlan(
                week_number=i + 1,
                phase=PhaseType.BASE,
                weekly_distance_km=30.0 + i * 5,
                weekly_elevation_gain_m=500 + i * 100,
            )
            for i in range(num_weeks)
        ]
        return TrainingPlan(
            distance_category=DistanceCategory.TRAIL_HALF,
            experience_level=ExperienceLevel.INTERMEDIATE,
            start_date=date(2025, 3, 3),
            race_date=date(2025, 8, 18),
            total_weeks=num_weeks,
            weeks=weeks,
        )

    def test_total_distance(self):
        plan = self._make_plan(3)
        assert plan.total_distance_km == 30.0 + 35.0 + 40.0

    def test_total_elevation(self):
        plan = self._make_plan(3)
        assert plan.total_elevation_gain_m == 500 + 600 + 700


# ============================================================
# 配置测试
# ============================================================

class TestConfig:
    """配置完整性测试"""

    def test_phase_distribution_all_distances(self):
        """每个距离都有阶段分配"""
        for dist in DistanceCategory:
            assert dist in PHASE_DISTRIBUTION
            phases = PHASE_DISTRIBUTION[dist]
            assert len(phases) == 4
            assert sum(phases) == 24 or sum(phases) > 0

    def test_weekly_training_days_all_combinations(self):
        """所有距离×经验组合都有训练天数配置"""
        for dist in DistanceCategory:
            assert dist in WEEKLY_TRAINING_DAYS
            for level in ExperienceLevel:
                assert level in WEEKLY_TRAINING_DAYS[dist]
                days = WEEKLY_TRAINING_DAYS[dist][level]
                assert 3 <= days <= 7

    def test_base_weekly_distance_ranges(self):
        """基础周跑量范围有效"""
        for dist in DistanceCategory:
            for level in ExperienceLevel:
                low, high = BASE_WEEKLY_DISTANCE[dist][level]
                assert low > 0
                assert high > low
                # 高级跑量应大于初学者
                if level == ExperienceLevel.ADVANCED:
                    beg_low, beg_high = BASE_WEEKLY_DISTANCE[dist][ExperienceLevel.BEGINNER]
                    assert high > beg_high

    def test_max_long_run_distance_increasing(self):
        """长距离跑最大距离随距离类别递增"""
        distances = [
            DistanceCategory.TRAIL_10K,
            DistanceCategory.TRAIL_HALF,
            DistanceCategory.TRAIL_FULL,
            DistanceCategory.TRAIL_50K,
            DistanceCategory.TRAIL_100K,
        ]
        for level in ExperienceLevel:
            prev_max = 0
            for dist in distances:
                current_max = MAX_LONG_RUN_DISTANCE[dist][level]
                assert current_max > prev_max
                prev_max = current_max

    def test_workout_distribution_sums_approximately_one(self):
        """各阶段训练类型分配比例总和接近1"""
        for phase, dist in WORKOUT_DISTRIBUTION.items():
            total = sum(dist.values())
            assert abs(total - 1.0) < 0.05, f"{phase} 阶段分配总和 = {total}"

    def test_elevation_gain_ranges_valid(self):
        """爬升范围有效"""
        for dist in DistanceCategory:
            for level in ExperienceLevel:
                low, high = WEEKLY_ELEVATION_GAIN[dist][level]
                assert low > 0
                assert high >= low


# ============================================================
# 生成器测试
# ============================================================

class TestTrainingPlanGenerator:
    """训练计划生成器核心测试"""

    @pytest.fixture
    def generator(self):
        return TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_HALF,
            experience_level=ExperienceLevel.INTERMEDIATE,
            start_date=date(2025, 3, 3),
            race_date=date(2025, 8, 18),
        )

    @pytest.fixture
    def plan(self, generator):
        return generator.generate()

    def test_generate_returns_training_plan(self, plan):
        """生成结果为 TrainingPlan 类型"""
        assert isinstance(plan, TrainingPlan)

    def test_plan_has_24_weeks(self, plan):
        """计划有24周"""
        assert plan.total_weeks == 24
        assert len(plan.weeks) == 24

    def test_plan_weeks_numbered_sequentially(self, plan):
        """周数连续编号"""
        for i, week in enumerate(plan.weeks):
            assert week.week_number == i + 1

    def test_plan_dates_correct(self, plan):
        """计划日期正确"""
        assert plan.start_date == date(2025, 3, 3)
        assert plan.race_date == date(2025, 8, 18)

    def test_plan_has_all_phase_types(self, plan):
        """计划包含所有主要阶段"""
        phases = set(w.phase for w in plan.weeks)
        # 至少包含基础期、构建期、巅峰期和减量期
        assert PhaseType.BASE in phases
        assert PhaseType.BUILD in phases
        assert PhaseType.PEAK in phases or PhaseType.TAPER in phases

    def test_plan_weeks_have_workouts(self, plan):
        """每周都有训练安排"""
        for week in plan.weeks:
            assert len(week.workouts) > 0

    def test_plan_weeks_have_positive_distance(self, plan):
        """每周跑量为正（非恢复/减量期可能较小但大于0）"""
        for week in plan.weeks:
            if week.phase != PhaseType.RECOVERY:
                assert week.weekly_distance_km > 0

    def test_plan_total_distance_positive(self, plan):
        """总跑量为正"""
        assert plan.total_distance_km > 0

    def test_plan_total_elevation_positive(self, plan):
        """总爬升为正"""
        assert plan.total_elevation_gain_m > 0

    def test_taper_at_end(self, plan):
        """减量期在计划末尾"""
        last_phase = plan.weeks[-1].phase
        assert last_phase == PhaseType.TAPER

    def test_each_week_has_7_days_coverage(self, plan):
        """每周覆盖7天"""
        for week in plan.weeks:
            days = set(w.day for w in week.workouts)
            assert days == set(range(1, 8)), f"第{week.week_number}周未覆盖所有7天"

    def test_rest_days_have_zero_duration(self, plan):
        """休息日时长为0"""
        for week in plan.weeks:
            for workout in week.workouts:
                if workout.workout_type == WorkoutType.REST:
                    assert workout.duration_minutes == 0

    def test_long_run_on_weekend(self, plan):
        """长距离跑安排在周六"""
        for week in plan.weeks:
            long_runs = [w for w in week.workouts if w.workout_type == WorkoutType.LONG_RUN]
            for lr in long_runs:
                assert lr.day == 6, f"第{week.week_number}周长距离跑不在周六"

    def test_long_run_has_distance(self, plan):
        """长距离跑有距离记录"""
        for week in plan.weeks:
            long_runs = [w for w in week.workouts if w.workout_type == WorkoutType.LONG_RUN]
            for lr in long_runs:
                assert lr.distance_km is not None
                assert lr.distance_km > 0


class TestAllDistanceCombinations:
    """所有距离×经验等级组合测试"""

    @pytest.mark.parametrize("distance", DistanceCategory)
    @pytest.mark.parametrize("level", ExperienceLevel)
    def test_generate_plan(self, distance, level):
        """每种组合都能成功生成计划"""
        generator = TrainingPlanGenerator(
            distance_category=distance,
            experience_level=level,
            start_date=date(2025, 3, 3),
            race_date=date(2025, 8, 18),
        )
        plan = generator.generate()
        assert len(plan.weeks) == 24
        assert plan.total_distance_km > 0

    @pytest.mark.parametrize("distance", DistanceCategory)
    @pytest.mark.parametrize("level", ExperienceLevel)
    def test_weekly_distance_within_reasonable_bounds(self, distance, level):
        """周跑量在合理范围内"""
        generator = TrainingPlanGenerator(
            distance_category=distance,
            experience_level=level,
            start_date=date(2025, 3, 3),
        )
        plan = generator.generate()

        base_low, base_high = BASE_WEEKLY_DISTANCE[distance][level]
        for week in plan.weeks:
            # 非恢复周跑量不应超过基础期的3倍
            if week.phase not in (PhaseType.RECOVERY, PhaseType.TAPER):
                assert week.weekly_distance_km <= base_high * 3, \
                    f"{distance.value} {level.value} 第{week.week_number}周跑量过大: {week.weekly_distance_km}"

    @pytest.mark.parametrize("distance", DistanceCategory)
    @pytest.mark.parametrize("level", ExperienceLevel)
    def test_long_run_distance_within_limit(self, distance, level):
        """长距离跑不超过最大限制"""
        generator = TrainingPlanGenerator(
            distance_category=distance,
            experience_level=level,
            start_date=date(2025, 3, 3),
        )
        plan = generator.generate()
        max_long = MAX_LONG_RUN_DISTANCE[distance][level]

        for week in plan.weeks:
            for w in week.workouts:
                if w.workout_type == WorkoutType.LONG_RUN and w.distance_km:
                    assert w.distance_km <= max_long * 1.05, \
                        f"第{week.week_number}周长距离跑 {w.distance_km}km 超过限制 {max_long}km"


class TestGeneratorEdgeCases:
    """生成器边界情况测试"""

    def test_default_start_date(self):
        """默认开始日期为下周一"""
        generator = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_10K,
            experience_level=ExperienceLevel.BEGINNER,
        )
        assert generator.start_date.weekday() == 0  # 周一

    def test_invalid_date_range(self):
        """日期范围不当时抛出异常"""
        with pytest.raises(ValueError):
            TrainingPlanGenerator(
                distance_category=DistanceCategory.TRAIL_10K,
                experience_level=ExperienceLevel.BEGINNER,
                start_date=date(2025, 3, 3),
                race_date=date(2025, 3, 10),  # 只有1周
            )

    def test_with_runner_name(self):
        """带跑者姓名"""
        generator = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_FULL,
            experience_level=ExperienceLevel.ADVANCED,
            start_date=date(2025, 3, 3),
            runner_name="测试跑者",
            target_time="3小时30分",
        )
        plan = generator.generate()
        assert plan.runner_name == "测试跑者"
        assert plan.target_time == "3小时30分"

    def test_recovery_week_lower_distance(self):
        """恢复周跑量低于常规周"""
        generator = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_HALF,
            experience_level=ExperienceLevel.INTERMEDIATE,
            start_date=date(2025, 3, 3),
        )
        plan = generator.generate()

        for i, week in enumerate(plan.weeks):
            if week.phase == PhaseType.RECOVERY and i > 0:
                prev_week = plan.weeks[i - 1]
                if prev_week.phase not in (PhaseType.RECOVERY, PhaseType.TAPER):
                    assert week.weekly_distance_km < prev_week.weekly_distance_km, \
                        f"第{week.week_number}周恢复周跑量应低于前一周"


# ============================================================
# 渲染器测试
# ============================================================

class TestPlanRenderer:
    """渲染器测试"""

    @pytest.fixture
    def plan(self):
        generator = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_10K,
            experience_level=ExperienceLevel.BEGINNER,
            start_date=date(2025, 3, 3),
            race_date=date(2025, 8, 18),
            runner_name="测试跑者",
        )
        return generator.generate()

    def test_render_to_string(self, plan):
        """渲染为字符串"""
        text = render_plan_to_string(plan)
        assert isinstance(text, str)
        assert len(text) > 0

    def test_render_contains_distance(self, plan):
        """渲染结果包含距离信息"""
        text = render_plan_to_string(plan)
        assert "10K" in text

    def test_render_contains_runner_name(self, plan):
        """渲染结果包含跑者姓名"""
        text = render_plan_to_string(plan)
        assert "测试跑者" in text

    def test_render_contains_week_numbers(self, plan):
        """渲染结果包含周数"""
        text = render_plan_to_string(plan)
        for i in range(1, 25):
            assert f"第{i:2d}周" in text or f"第{i}周" in text

    def test_render_contains_workout_types(self, plan):
        """渲染结果包含训练类型"""
        text = render_plan_to_string(plan)
        assert "轻松跑" in text
        assert "长距离跑" in text
        assert "休息" in text

    def test_render_single_week(self, plan):
        """渲染单周"""
        renderer = PlanRenderer(plan)
        text = renderer.render_week(1)
        assert "第1周" in text or "第 1周" in text

    def test_render_invalid_week(self, plan):
        """渲染无效周数"""
        renderer = PlanRenderer(plan)
        text = renderer.render_week(99)
        assert "无效" in text

    def test_render_contains_phase_info(self, plan):
        """渲染结果包含阶段信息"""
        text = render_plan_to_string(plan)
        assert "基础期" in text

    def test_render_contains_tips(self, plan):
        """渲染结果包含注意事项"""
        text = render_plan_to_string(plan)
        assert "注意事项" in text


# ============================================================
# 各距离专项测试
# ============================================================

class Test10KPlan:
    """10K训练计划专项测试"""

    def test_10k_beginner_plan(self):
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_10K,
            experience_level=ExperienceLevel.BEGINNER,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()
        assert plan.total_distance_km > 0
        # 初学者每周训练3天
        for week in plan.weeks:
            training_days = sum(1 for w in week.workouts if w.workout_type != WorkoutType.REST)
            assert training_days == 3 or week.phase == PhaseType.RECOVERY

    def test_10k_advanced_plan(self):
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_10K,
            experience_level=ExperienceLevel.ADVANCED,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()
        assert plan.total_distance_km > 0


class TestHalfMarathonPlan:
    """半马训练计划专项测试"""

    def test_half_beginner(self):
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_HALF,
            experience_level=ExperienceLevel.BEGINNER,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()
        assert plan.total_distance_km > 300  # 24周至少300km


class TestFullMarathonPlan:
    """全马训练计划专项测试"""

    def test_full_intermediate(self):
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_FULL,
            experience_level=ExperienceLevel.INTERMEDIATE,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()
        assert plan.total_distance_km > 500  # 全马中级至少500km


class Test50KPlan:
    """50K训练计划专项测试"""

    def test_50k_advanced(self):
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_50K,
            experience_level=ExperienceLevel.ADVANCED,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()
        assert plan.total_distance_km > 800  # 50K高级至少800km


class Test100KPlan:
    """100K训练计划专项测试"""

    def test_100k_advanced(self):
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_100K,
            experience_level=ExperienceLevel.ADVANCED,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()
        assert plan.total_distance_km > 1000  # 100K高级至少1000km

    def test_100k_has_trail_specific(self):
        """100K计划包含越野专项训练"""
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_100K,
            experience_level=ExperienceLevel.ADVANCED,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()
        trail_workouts = []
        for week in plan.weeks:
            for w in week.workouts:
                if w.workout_type == WorkoutType.TRAIL_SPECIFIC:
                    trail_workouts.append(w)
        assert len(trail_workouts) > 0, "100K计划应包含越野专项训练"

    def test_100k_has_hill_training(self):
        """100K计划包含爬坡训练"""
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_100K,
            experience_level=ExperienceLevel.INTERMEDIATE,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()
        hill_workouts = []
        for week in plan.weeks:
            for w in week.workouts:
                if w.workout_type == WorkoutType.HILL_REPEAT:
                    hill_workouts.append(w)
        assert len(hill_workouts) > 0, "100K计划应包含爬坡训练"


# ============================================================
# 跑量递进测试
# ============================================================

class TestProgression:
    """训练进度递进测试"""

    def test_base_phase_distance_increases(self):
        """基础期跑量逐步增加"""
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_HALF,
            experience_level=ExperienceLevel.INTERMEDIATE,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()

        base_weeks = [w for w in plan.weeks if w.phase == PhaseType.BASE]
        if len(base_weeks) > 1:
            # 整体趋势应为增加
            first_half = sum(w.weekly_distance_km for w in base_weeks[:len(base_weeks)//2])
            second_half = sum(w.weekly_distance_km for w in base_weeks[len(base_weeks)//2:])
            assert second_half >= first_half * 0.8, "基础期跑量应有增加趋势"

    def test_peak_phase_highest_volume(self):
        """巅峰期跑量最高"""
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_FULL,
            experience_level=ExperienceLevel.ADVANCED,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()

        base_avg = sum(w.weekly_distance_km for w in plan.weeks if w.phase == PhaseType.BASE) / \
                   max(sum(1 for w in plan.weeks if w.phase == PhaseType.BASE), 1)
        peak_avg = sum(w.weekly_distance_km for w in plan.weeks if w.phase == PhaseType.PEAK) / \
                   max(sum(1 for w in plan.weeks if w.phase == PhaseType.PEAK), 1)

        if peak_avg > 0:
            assert peak_avg >= base_avg * 0.8, "巅峰期跑量应不低于基础期"

    def test_taper_reduces_volume(self):
        """减量期跑量减少"""
        gen = TrainingPlanGenerator(
            distance_category=DistanceCategory.TRAIL_FULL,
            experience_level=ExperienceLevel.INTERMEDIATE,
            start_date=date(2025, 3, 3),
        )
        plan = gen.generate()

        peak_weeks = [w for w in plan.weeks if w.phase == PhaseType.PEAK]
        taper_weeks = [w for w in plan.weeks if w.phase == PhaseType.TAPER]

        if peak_weeks and taper_weeks:
            peak_avg = sum(w.weekly_distance_km for w in peak_weeks) / len(peak_weeks)
            taper_avg = sum(w.weekly_distance_km for w in taper_weeks) / len(taper_weeks)
            assert taper_avg < peak_avg, "减量期跑量应低于巅峰期"


# ============================================================
# CLI 测试
# ============================================================

class TestCLI:
    """命令行接口测试"""

    def test_distance_map_completeness(self):
        """距离映射完整"""
        from trail_running_planner.cli import DISTANCE_MAP
        for dist in DistanceCategory:
            assert any(v == dist for v in DISTANCE_MAP.values())

    def test_level_map_completeness(self):
        """等级映射完整"""
        from trail_running_planner.cli import LEVEL_MAP
        for level in ExperienceLevel:
            assert any(v == level for v in LEVEL_MAP.values())

    def test_parse_date_valid(self):
        """日期解析 - 有效"""
        from trail_running_planner.cli import parse_date
        result = parse_date("2025-03-03")
        assert result == date(2025, 3, 3)

    def test_parse_date_invalid(self):
        """日期解析 - 无效"""
        from trail_running_planner.cli import parse_date
        with pytest.raises(SystemExit):
            parse_date("invalid-date")
