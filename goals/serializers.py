from typing import Dict

from django.db import transaction
from rest_framework import serializers

from core.models import User
from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_board(self, value: Board) -> Board:
        if value.is_deleted:
            raise serializers.ValidationError("Нельзя использовать удаленные доски")

        validated_users = BoardParticipant.objects.filter(
            user=self.context["request"].user,
            board=value,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]).exists()

        if not validated_users:
            raise serializers.ValidationError("Нельзя редактировать категории на чужой доске или при роли Читатель")

        return value


class GoalCategorySerializer(GoalCategoryCreateSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "board")
        fields = "__all__"


class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_category(self, value: GoalCategory) -> GoalCategory:
        if value.is_deleted:
            raise serializers.ValidationError("Нельзя использовать удаленные категории")

        validated_users = BoardParticipant.objects.filter(
            user=self.context["request"].user,
            board=value.board,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]).exists()

        if not validated_users:
            raise serializers.ValidationError("Нельзя редактировать цели на чужой доске или при роли Читатель")

        return value


class GoalSerializer(GoalCreateSerializer):
    user = UserSerializer(read_only=True)


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise serializers.ValidationError("Нельзя комментировать удаленные цели")

        validated_users = BoardParticipant.objects.filter(
            user=self.context["request"].user,
            board=value.category.board,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]).exists()

        if not validated_users:
            raise serializers.ValidationError("Нельзя писать комментарии при роли Читатель")

        return value


class GoalCommentSerializer(GoalCommentCreateSerializer):
    user = UserSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)


class BoardCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated")
        fields = "__all__"

    def create(self, validated_data: Dict) -> Board:
        user = validated_data.pop("user")
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(
            user=user, board=board, role=BoardParticipant.Role.owner
        )
        return board


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        required=True, choices=BoardParticipant.Role.choices[1:]
    )
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


class BoardSerializer(serializers.ModelSerializer):
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")

    def update(self, instance: Board, validated_data: Dict) -> Board:
        owner = validated_data.pop("user")
        old_participants = instance.participants.exclude(user=owner)
        new_participants = validated_data.pop("participants")
        new_part_with_id = {}
        for participant in new_participants:
            new_part_with_id[participant["user"].id] = participant

        with transaction.atomic():
            for old_participant in old_participants:
                if old_participant.user_id not in new_part_with_id:
                    old_participant.delete()
                else:
                    if old_participant.role != new_part_with_id[old_participant.user_id]["role"]:
                        old_participant.role = new_part_with_id[old_participant.user_id]["role"]
                    old_participant.save()
                new_part_with_id.pop(old_participant.user_id)

            for new_participant in new_part_with_id.values():
                BoardParticipant.objects.create(
                    user=new_participant['user'],
                    board=instance, role=new_participant['role'])

        instance.title = validated_data["title"]
        instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = "__all__"
