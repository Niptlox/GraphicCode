import pygame as pg

pg.font.init()


class StyleSheet:
    class Block:
        MainFontPath = "fonts/DePixelSchmal.ttf"
        MainFontSize = 12
        MainFont = pg.font.Font(MainFontPath, MainFontSize)
        MainColor = "#222034"
        BorderColor = "#3c395b"
        MainTextColor = "#99e550"
        Text2Color = "#fbf236"
        MiddleWidth = 100

    class Connection:
        RunColor = "#ffffff"
        BoolTypeColor = "#6abe30"
        IntTypeColor = "#5b6ee1"
        StrTypeColor = "#fbf236"
        ObjectTypeColor = "#ac3232"


style_sheet = StyleSheet()


def gen_block_value(width, name, inputs, outputs, run_outputs=[], run_block=False):
    top_h = 20
    name_bar_offset = 18
    val_step = 20
    width_to_text = 18
    y_cnt = max(len(outputs + run_outputs), len(inputs))
    height = top_h + 5 + y_cnt * val_step + 5

    surface = pg.Surface((width, height))
    surface.fill(style_sheet.Block.MainColor)
    pg.draw.rect(surface, style_sheet.Block.BorderColor, (0, 0, width, height), 2)
    s_name = style_sheet.Block.MainFont.render(name, True, style_sheet.Block.MainTextColor)

    bar_w = width - name_bar_offset * 2
    pg.draw.rect(surface, style_sheet.Block.BorderColor, ((width - bar_w) // 2, 0, bar_w, top_h))
    surface.blit(s_name, ((width - s_name.get_width()) // 2, 4))
    run_outputs_pos = []
    run_input_pos = None
    if run_block:
        run_input_pos = (4, 4)
        run_outputs_pos = [(width - 15, 4)]
    inputs_pos = []
    y = top_h + 10
    for st in inputs:
        val_name = style_sheet.Block.MainFont.render(st, True, style_sheet.Block.MainTextColor)
        surface.blit(val_name, (width_to_text + 2, y))
        inputs_pos.append((5, y))
        y += val_step

    outputs_pos = []
    y = top_h + 10

    if run_outputs:
        for st in run_outputs:
            val_name = style_sheet.Block.MainFont.render(st, True, style_sheet.Block.MainTextColor)
            surface.blit(val_name, (width - width_to_text - val_name.get_width(), y))
            run_outputs_pos.append((width - 15, y))
            y += val_step

    for st in outputs:
        val_name = style_sheet.Block.MainFont.render(st, True, style_sheet.Block.MainTextColor)
        surface.blit(val_name, (width - width_to_text - val_name.get_width(), y))
        outputs_pos.append((width - 15, y))
        y += val_step

    return surface, inputs_pos, outputs_pos, run_input_pos, run_outputs_pos
