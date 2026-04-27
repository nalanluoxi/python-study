
from pathlib import Path
import re
import yaml
class SkillLoader:
    def __init__(self, skills_dir: Path):
        print("skills_dir:", skills_dir)
        self.skills_dir = skills_dir
        self.skills = {}
        self._load_all()

    def _load_all(self):
        if not self.skills_dir.exists():
            return
        for f in sorted(self.skills_dir.rglob("SKILL.md")):
            text = f.read_text()
            meta,body = self._parse_frontmatter(text)
            name = meta.get("name", f.parent.name)
            descr = meta.get("description", "No description")
            self.skills[name] = {
                "name": name,
                "meta": meta,
                "description": descr,
                "body": body,
                "path":str(f),
            }
            #self.skills[name] = {"meta": meta, "body": body, "path": str(f)}

    def get_skillName(self)->str:
        if not self.skills:
            return "Error: No skills loaded"
        lines=[]
        for name, skill in self.skills.items():
            desc = skill["meta"].get("description", "No description")
            tags = skill["meta"].get("tags", "")
            line = f"  - {name}: {desc}"
            if tags:
                line += f" [{tags}]"
            lines.append(line)
        return "\n".join(lines)





    def _parse_frontmatter(self, text: str) -> tuple:
        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
        if not match:
            return  {} ,text
        try:
            safe_load = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            safe_load = {}
       # print("测试查看正则匹配到的内容")
       # for i in range(len(match)):
       #     print(i+"的内容是:["+match.group(i))
        return safe_load, match.group(2).strip()

    def get_content(self, name: str) -> str:
        skill = self.skills.get(name)
        if not skill:
            return f"Error: Unknown skill '{name}'. Available: {', '.join(self.skills.keys())}"
        return f"<skill name=\"{name}\">\n{skill['body']}\n</skill>"

