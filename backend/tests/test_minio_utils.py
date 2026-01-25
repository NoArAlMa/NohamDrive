from types import SimpleNamespace
from app.utils.minio_utils import MinioUtils


def fake_objects(*names):
    return [SimpleNamespace(object_name=name) for name in names]


def test_generate_name_no_conflict(mocker):
    minio = mocker.Mock()
    minio.list_objects.return_value = fake_objects()

    result = MinioUtils.generate_available_name(
        minio,
        bucket_name="test",
        base_name="lili.txt",
    )
    print("INPUT:", ["lili.txt"])
    print("OUTPUT:", result)
    assert result == "lili.txt"


def test_generate_name_first_conflict(mocker):
    minio = mocker.Mock()
    minio.list_objects.return_value = fake_objects("lili.txt")

    result = MinioUtils.generate_available_name(
        minio,
        bucket_name="test",
        base_name="lili.txt",
    )
    print("INPUT:", ["lili.txt"])
    print("OUTPUT:", result)
    assert result == "lili (1).txt"


def test_generate_name_increment_suffix(mocker):
    minio = mocker.Mock()
    minio.list_objects.return_value = fake_objects(
        "lili.txt",
        "lili (1).txt",
    )

    result = MinioUtils.generate_available_name(
        minio,
        bucket_name="test",
        base_name="lili.txt",
    )
    print("INPUT:", ["lili (1).txt"])
    print("OUTPUT:", result)
    assert result == "lili (2).txt"


def test_generate_name_from_suffixed_input(mocker):
    minio = mocker.Mock()
    minio.list_objects.return_value = fake_objects(
        "lili.txt",
        "lili (1).txt",
    )

    result = MinioUtils.generate_available_name(
        minio,
        bucket_name="test",
        base_name="lili (1).txt",
    )
    print("INPUT:", ["lili (1).txt"])
    print("OUTPUT:", result)

    assert result == "lili (2).txt"


def test_generate_name_with_parent_path(mocker):
    minio = mocker.Mock()
    minio.list_objects.return_value = fake_objects(
        "folder/lili.txt",
        "folder/lili (1).txt",
    )

    result = MinioUtils.generate_available_name(
        minio,
        bucket_name="test",
        base_name="lili.txt",
        parent_path="folder",
    )

    print("INPUT:", ["folder/lili (1).txt"])
    print("OUTPUT:", result)

    assert result == "folder/lili (2).txt"


def test_generate_folder_name(mocker):
    minio = mocker.Mock()
    minio.list_objects.return_value = fake_objects(
        "docs/",
        "docs (1)/",
    )

    result = MinioUtils.generate_available_name(
        minio,
        bucket_name="test",
        base_name="docs/",
        is_folder=True,
    )
    print("INPUT:", ["docs/", "docs (1)/"])
    print("OUTPUT:", result)

    assert result == "docs (2)/"
