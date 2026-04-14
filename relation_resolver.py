import json


class RelationResolver:
    def __init__(self, path):
        self.data = json.load(open(path, encoding="utf-8"))

    def resolve(self, target, related, context=None):
        res = []
        context = context or {}
        queue = [target]
        visited = set()

        while queue:
            source = queue.pop(0)
            if source in visited:
                continue
            visited.add(source)

            for r in self.data.get(source, {}).values():
                for i in r:
                    if target == i["target"]:
                        continue

                    cond = i.get("condition")
                    if cond and cond not in context.get("conditions", []):
                        continue

                    if source != target or i["target"] in related:
                        res.append({
                            "source": source,
                            "target": i["target"],
                            "text": i["text"],
                        })
                        queue.append(i["target"])
        return res
