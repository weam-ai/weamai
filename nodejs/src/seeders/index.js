const seedService = require('../services/seeder');

async function initSeed () {
    try {
        // await seedService.seedEmailTemplate();
        await seedService.seedRole();
        // await seedService.seedAdmin();
        // await seedService.seedNotification();
        // await seedService.seedSetting();
        // await seedService.seedDefaultModel();
        // await seedService.seedCustomGPT();
        // await seedService.seedPrompt();
        await seedService.seedOtherRolePermission();
        // await seedService.migrateUser();
        // await seedService.freeWeamApiMigration();
        // await seedService.queryLimitKeyMigration()
        // await seedService.botMigration()
        // await seedService.seedCountry();
        // await seedService.seedCompanyCountryCode();
        // await seedService.seedGeneralBrain();
        await seedService.seedMigrateBlockedDomains();
    } catch (error) {
        logger.error('Error in initSeed function', error);
        
    }
}

module.exports = initSeed;