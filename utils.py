import unicodedata


LINEBREAK_LENGTH = 55


def insert_linebreak_text(text: str):
    length = 1
    comb_flag = False
    comb_cache = 0
    for idx, char in enumerate(text):
        if char == "\\":
            comb_flag = True
            length += 1
            comb_cache += 1
            continue

        elif comb_flag and char == "]":
            comb_flag = False
            length += 1
            comb_cache += 1

            if length == LINEBREAK_LENGTH:  # 需要换行
                text = f"{text[:idx+1]}<br>{text[idx+1:]}"
                break
            elif length > LINEBREAK_LENGTH:  # 需要在之前就换行
                text = f"{text[:idx+1-comb_cache]}<br>{text[idx+1-comb_cache:]}"
                break
            comb_cache = 0
            continue

        elif comb_flag:
            length += 1
            comb_cache += 1
            continue

        cache = 0
        if unicodedata.east_asian_width(char) in "FWA":
            length += 2
            cache += 2
        else:
            length += 1
            cache += 1

        if length == LINEBREAK_LENGTH:
            text = f"{text[:idx+1]}<br>{text[idx+1:]}"
            break
        elif length > LINEBREAK_LENGTH:
            text = f"{text[:idx+1-cache]}<br>{text[idx+1-cache:]}"
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