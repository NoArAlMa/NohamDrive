from app.utils.user_utils import UserUtils


def test_get_initials_from_full_name_uses_first_and_last_word():
    assert UserUtils.get_initials_from_full_name("Jean Pierre") == "JP"
    assert UserUtils.get_initials_from_full_name("  Jean   Pierre  Dubois ") == "JD"


def test_get_initials_from_full_name_single_word_uses_two_letters_when_possible():
    assert UserUtils.get_initials_from_full_name("alice") == "AL"
    assert UserUtils.get_initials_from_full_name("É") == "É"


def test_generate_profile_picture_svg_contains_initials_and_title():
    svg = UserUtils.generate_profile_picture_svg("Jean Pierre")
    assert "<svg" in svg
    assert ">JP<" in svg
    assert "<title" in svg and "Jean Pierre" in svg

