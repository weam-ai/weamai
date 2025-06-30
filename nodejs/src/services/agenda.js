const agenda = require('../config/agenda');
const User = require('../models/user');
const { AGENDA_CRON, INVITATION_TYPE } = require('../config/constants/common');

agenda.define(
    AGENDA_CRON.PROMPT_PER_DAY,
    {
        concurrency: 1,
        priority: 20,
    },
    async () => {
        logger.info(
            `Start ${AGENDA_CRON.PROMPT_PER_DAY} Agenda process at ${convertToTz()}`,
        );
        // reset message 0 per day
        await User.updateMany({}, { $set: { 'promptLimit.usedByDay': 0 } });
        logger.info(
            `finish ${AGENDA_CRON.PROMPT_PER_DAY} Agenda process at ${convertToTz()}`,
        );
    },
);

agenda.define(
    AGENDA_CRON.PROMPT_PER_WEEK,
    {
        concurrency: 1,
        priority: 20,
    },
    async () => {
        logger.info(
            `Start ${AGENDA_CRON.PROMPT_PER_WEEK} Agenda process at ${convertToTz()}`,
        );
        // reset message 0 per week
        await User.updateMany({}, { $set: { 'promptLimit.usedByWeek': 0} })
        logger.info(
            `finish ${AGENDA_CRON.PROMPT_PER_WEEK} Agenda process at ${convertToTz()}`,
        );
    },
);

agenda.define(
    AGENDA_CRON.PROMPT_PER_MONTH,
    {
        concurrency: 1,
        priority: 20,
    },
    async () => {
        logger.info(
            `Start ${AGENDA_CRON.PROMPT_PER_MONTH} Agenda process at ${convertToTz()}`,
        );
        // reset message 0 per month
        await User.updateMany({}, { $set: { 'promptLimit.usedByMonth': 0 } })
        logger.info(
            `finish ${AGENDA_CRON.PROMPT_PER_MONTH} Agenda process at ${convertToTz()}`,
        );
    },
);

agenda.define(
    AGENDA_CRON.INVITATION_MEMBER_STATUS,
    {
        concurrency: 1,
        priority: 20,
    },
    async () => {
        logger.info(
            `Start ${AGENDA_CRON.INVITATION_MEMBER_STATUS} Agenda process at ${convertToTz()}`,
        );
        // update link expire status
        
        const users = await User.find({
            inviteExpireOn: { $exists: true },
            invited: true,
            $expr: {
                $lt: [
                    { $dateFromString: { dateString: '$inviteExpireOn', format: '%Y-%m-%d %H:%M:%S' } },
                    new Date()
                ],
            }
        })
    
        await User.updateMany({
            inviteExpireOn: { $exists: true },
            $expr: {
                $lt: [
                    { $dateFromString: { dateString: '$inviteExpireOn', format: '%Y-%m-%d %H:%M:%S' } },
                    new Date()
                ],
            }
        }, {  
            $unset: {
                inviteLink: 1,
                inviteExpireOn: 1,
            },
            $set: {
                inviteSts: INVITATION_TYPE.EXPIRED
            }
        })

        logger.info(
            `finish ${AGENDA_CRON.INVITATION_MEMBER_STATUS} Agenda process at ${convertToTz()}`,
        );
    },
);


async function resetPromptDay() {
    await agenda.start();
    await agenda.every('0 0 * * *', AGENDA_CRON.PROMPT_PER_DAY);
}

async function resetPromptWeek() {
    await agenda.start();
    await agenda.every('0 0 * * 1', AGENDA_CRON.PROMPT_PER_WEEK);
}

async function resetPromptMonth() {
    await agenda.start();
    await agenda.every('0 0 1 * *', AGENDA_CRON.PROMPT_PER_MONTH);
}

async function checkInviteMemberStatus() {
    await agenda.start();
    await agenda.every('0 0 * * *', AGENDA_CRON.INVITATION_MEMBER_STATUS);
}

// resetPromptDay();
// resetPromptWeek();
// resetPromptMonth();
checkInviteMemberStatus();