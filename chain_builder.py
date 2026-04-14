class ChainBuilder:
    def build(self, relations):
        if not relations:
            return [], None

        chains = []

        for r in relations:
            chain = [r]
            current = r
            used_targets = {r["target"]}

            while True:
                found = False
                for nxt in relations:
                    if nxt["target"] in used_targets:
                        continue

                    if nxt["source"] == current["target"]:
                        chain.append(nxt)
                        used_targets.add(nxt["target"])
                        current = nxt
                        found = True
                        break

                if not found:
                    break

            chains.append(chain)

        def score(chain):
            branch_penalty = sum(
                1
                for item in chain
                for other in relations
                if other is not item and other["source"] == item["source"]
            )
            condition_bonus = sum(1 for item in chain if item.get("condition"))
            return len(chain) + condition_bonus - branch_penalty

        best = max(chains, key=score)
        reason = f"가장 긴 인과 경로 선택 (length={len(best)})"

        return [c["text"] for c in best], reason
