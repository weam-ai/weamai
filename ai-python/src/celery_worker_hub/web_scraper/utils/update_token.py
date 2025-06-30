def update_tokens(summary_data: dict, existing_doc: dict) -> dict:
    if existing_doc:
        tokens_old = existing_doc.get('tokens', {})
        total_old_cost = float(tokens_old.get('totalCost', "0").replace("$", ""))
        prompt_t = tokens_old.get('promptT', 0)
        total_used = tokens_old.get("totalUsed", 0)
        total_completion_token = tokens_old.get("completion", 0)
    else:
        total_old_cost = 0.0
        prompt_t = 0
        total_used = 0
        total_completion_token = 0

    cal_cost =summary_data['$set']['tokens.totalCost'] + total_old_cost
    cal_promptT = summary_data['$set']['tokens.promptT'] + prompt_t
    cal_total_used = summary_data['$set']['tokens.totalUsed'] + total_used
    cal_total_completion_token = summary_data['$set']['tokens.completion'] + total_completion_token

    summary_data['$set']['tokens.totalCost'] = f"${cal_cost}"
    summary_data['$set']['tokens.promptT'] = cal_promptT
    summary_data['$set']['tokens.totalUsed'] = cal_total_used
    summary_data['$set']['tokens.completion'] = cal_total_completion_token
    summary_data['$set']["isCompleted"]=True
    return summary_data


def update_child_tokens(summary_data: dict) -> dict:
    summary_data['$set']['tokens.totalCost'] = f"$0.000"
    summary_data['$set']['tokens.promptT'] = 0
    summary_data['$set']['tokens.totalUsed'] = 0
    summary_data['$set']['tokens.completion'] = 0
    summary_data['$set']["isCompleted"]=True
    return summary_data