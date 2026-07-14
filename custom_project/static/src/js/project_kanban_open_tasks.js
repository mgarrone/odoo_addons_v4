/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { KanbanRecord } from "@web/views/kanban/kanban_record";

async function openProjectTasks(env, resId) {
    const action = await env.services.orm.call(
        "project.project",
        "action_open_project_tasks",
        [resId]
    );
    await env.services.action.doAction(action);
}

patch(KanbanRecord.prototype, {
    async onClick(ev) {
        const record = this.props.record;
        const model = this.props.record?.model?.root?.resModel || this.props.record?.modelName;
        if (model === "project.project" && record?.resId) {
            ev.preventDefault();
            ev.stopPropagation();
            await openProjectTasks(this.env, record.resId);
            return;
        }
        return super.onClick(ev);
    },
});
