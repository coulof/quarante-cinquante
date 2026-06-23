extends Node
## Autoload singleton. Holds persistent progression and saves/loads it through
## the browser's localStorage via JavaScriptBridge (user:// does not persist on web).

signal weapon_unlocked(weapon_id: String)
signal skin_unlocked(skin_id: String)
signal skin_changed(skin_id: String)
signal progress_loaded

const SAVE_KEY := "beatemall_save_v2"

# --- Persisted fields ---------------------------------------------------------
var unlocked_weapons: Array[String] = ["pickaxe"]
var unlocked_skins: Array[String] = ["hero_default"]
var active_skin: String = "hero_default"
var highest_level: int = 1


func _ready() -> void:
	load_progress()


# --- Mutators -----------------------------------------------------------------
func unlock_weapon(weapon_id: String) -> void:
	if weapon_id.is_empty() or weapon_id in unlocked_weapons:
		return
	unlocked_weapons.append(weapon_id)
	weapon_unlocked.emit(weapon_id)
	save()


func unlock_skin(skin_id: String) -> void:
	if skin_id.is_empty() or skin_id in unlocked_skins:
		return
	unlocked_skins.append(skin_id)
	skin_unlocked.emit(skin_id)
	save()


func set_active_skin(skin_id: String) -> void:
	if skin_id not in unlocked_skins:
		return
	active_skin = skin_id
	skin_changed.emit(skin_id)
	save()


func reach_level(level: int) -> void:
	if level <= highest_level:
		return
	highest_level = level
	save()


func has_weapon(weapon_id: String) -> bool:
	return weapon_id in unlocked_weapons


# --- Serialisation ------------------------------------------------------------
func _to_dict() -> Dictionary:
	return {
		"unlocked_weapons": unlocked_weapons,
		"unlocked_skins": unlocked_skins,
		"active_skin": active_skin,
		"highest_level": highest_level,
	}


func _from_dict(data: Dictionary) -> void:
	# Arrays come back from JSON as untyped Array; convert explicitly.
	var weapons: Array[String] = []
	for w in data.get("unlocked_weapons", ["pickaxe"]):
		weapons.append(str(w))
	var skins: Array[String] = []
	for s in data.get("unlocked_skins", ["hero_default"]):
		skins.append(str(s))

	unlocked_weapons = weapons if not weapons.is_empty() else ["pickaxe"] as Array[String]
	unlocked_skins = skins if not skins.is_empty() else ["hero_default"] as Array[String]
	active_skin = str(data.get("active_skin", "hero_default"))
	highest_level = int(data.get("highest_level", 1))


# --- Persistence (localStorage on web, user:// elsewhere) ---------------------
func save() -> void:
	var json := JSON.stringify(_to_dict())
	if OS.has_feature("web"):
		# Escape for safe embedding inside a JS string literal.
		var safe := json.json_escape()
		JavaScriptBridge.eval("localStorage.setItem('%s', \"%s\");" % [SAVE_KEY, safe], true)
	else:
		var f := FileAccess.open("user://%s.json" % SAVE_KEY, FileAccess.WRITE)
		if f:
			f.store_string(json)
			f.close()


func load_progress() -> void:
	var json := ""
	if OS.has_feature("web"):
		var raw = JavaScriptBridge.eval("localStorage.getItem('%s');" % SAVE_KEY, true)
		if raw != null:
			json = str(raw)
	else:
		if FileAccess.file_exists("user://%s.json" % SAVE_KEY):
			var f := FileAccess.open("user://%s.json" % SAVE_KEY, FileAccess.READ)
			if f:
				json = f.get_as_text()
				f.close()

	if json.is_empty():
		progress_loaded.emit()
		return

	var parsed = JSON.parse_string(json)
	if parsed is Dictionary:
		_from_dict(parsed)
	progress_loaded.emit()


func reset() -> void:
	unlocked_weapons = ["pickaxe"]
	unlocked_skins = ["hero_default"]
	active_skin = "hero_default"
	highest_level = 1
	save()
