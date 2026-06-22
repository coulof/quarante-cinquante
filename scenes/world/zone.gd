extends Resource
class_name Zone
## A single combat zone within a level: which enemy, how many, and what comes next.
## Chaining zones via `next_zone` lets a level be a sequence of waves; the
## camera scroll target is stubbed now for future side-scrolling support.

@export var enemy_scene: PackedScene
@export var enemy_count: int = 5
@export var spawn_interval: float = 1.0
## null = level complete after this zone is cleared.
@export var next_zone: Zone
## Reserved for Phase 2 camera scrolling; not activated this session.
@export var camera_target_x: float = 0.0
