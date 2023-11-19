import unicodedata


def insert_linebreak_text(text: str, linebreak: str = "<br>", linebreak_length: int = 55):
    length = 1
    comb_flag = False
    comb_cache = 0
    for idx, char in enumerate(text):
        if char == "\\" and text[idx+1] in "ic":  # \n 名称是有字数的
            comb_flag = True
            # length += 1
            comb_cache += 1
            continue

        elif comb_flag and char == "]":
            comb_flag = False
            # length += 1
            comb_cache += 1

            # if length == linebreak_length:  # 需要换行
            #     text = f"{text[:idx+1]}{linebreak}{text[idx+1:]}"
            #     break
            # elif length > linebreak_length:  # 需要在之前就换行
            #     text = f"{text[:idx+1-comb_cache]}{linebreak}{text[idx+1-comb_cache:]}"
            #     break
            continue

        elif comb_flag:
            # length += 1
            comb_cache += 1
            continue

        cache = 0
        if unicodedata.east_asian_width(char) in "FWA":
            length += 2
            cache += 2
        else:
            length += 1
            cache += 1

        if length == linebreak_length:
            text = f"{text[:idx+1]}{linebreak}{text[idx+1:]}"
            break
        elif length > linebreak_length:
            text = f"{text[:idx+1-cache]}{linebreak}{text[idx+1-cache:]}"
            break

    return text


def main():
    line = "这是我的\c[12]手机\c[0]。\c[2]快捷键\c[0]是\c[12]P\c[0]。里面有很多有用的功能。"
    print(insert_linebreak_text(line))


__all__ = [
    "insert_linebreak_text"
]


if __name__ == '__main__':
    main()