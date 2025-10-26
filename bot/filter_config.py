import json
import bot.image_filters

filter_functions = {
    "grayscale": bot.image_filters.grayscale,
    "sepia": bot.image_filters.sepia,
    "invert": bot.image_filters.invert,
    "gaussian": bot.image_filters.gaussian,
    "median": bot.image_filters.median,
    "sharpen": bot.image_filters.sharpen,
    "brightness": bot.image_filters.brightness,
    "saturation": bot.image_filters.saturation,
    "color_balance": bot.image_filters.color_balance,
    "vignette": bot.image_filters.vignette,
    "add_noise": bot.image_filters.add_noise,
    "pixel_art": bot.image_filters.pixel_art,
    "fisheye": bot.image_filters.fisheye,
}


class FilterConfig:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.filter_groups = self.config["filter_groups"]
        self.filters = {f["name"]: f for f in self.config["filters"]}

    def get_group_filters(self, group: str):
        return [f for f in self.config["filters"] if f["group"] == group]

    def get_filter(self, filter_name: str):
        return self.filters.get(filter_name)

    def filter_requires_parameters(self, filter_name: str) -> bool:
        filter_data = self.get_filter(filter_name)
        return filter_data.get("has_parameters", False) if filter_data else False


filter_config = FilterConfig("bot/filter_config.json")
