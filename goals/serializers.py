from rest_framework import serializers

from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal, GoalComment


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"


class GoalCategorySerializer(GoalCategoryCreateSerializer):
    user = UserSerializer(read_only=True)


class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_category(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("Нельзя использовать удаленные категории")

        if value.user != self.context["request"].user:
            raise serializers.ValidationError("Нельзя использовать чужие категории целей")

        return value


class GoalSerializer(GoalCreateSerializer):
    user = UserSerializer(read_only=True)


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_goal(self, value):
        if value.status == Goal.Status.archived:
            raise serializers.ValidationError("Нельзя комментировать удаленные цели")

        if value.user != self.context["request"].user:
            raise serializers.ValidationError("Нельзя комментировать чужие цели")

        return value


class GoalCommentSerializer(GoalCommentCreateSerializer):
    user = UserSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)
