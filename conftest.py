"""pytest 根配置：把项目根目录加入 sys.path，保证 common/api/pages 可导入。"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
