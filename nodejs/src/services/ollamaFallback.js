const ollamaService = require('../services/ollamaService');

class OllamaFallbackService {
    constructor() {
        this.fallbackEnabled = process.env.OLLAMA_FALLBACK_ENABLED === 'true';
        this.fallbackProviders = ['openai', 'anthropic', 'azure'];
    }

    async chatWithFallback(chatParams, userId, companyId) {
        const startTime = Date.now();
        
        try {
            const result = await ollamaService.chat(chatParams);
            
            if (result.success) {
                await this.trackSuccessfulRequest(chatParams.model, Date.now() - startTime);
                return result;
            }
            
            throw new Error(result.error);
            
        } catch (error) {
            logger.warn(`Ollama request failed for model ${chatParams.model}:`, error.message);
            
            if (this.fallbackEnabled) {
                return await this.handleFallback(chatParams, userId, companyId, 'chat', error);
            }
            
            throw error;
        }
    }

    async generateWithFallback(generateParams, userId, companyId) {
        const startTime = Date.now();
        
        try {
            const result = await ollamaService.generate(generateParams);
            
            if (result.success) {
                await this.trackSuccessfulRequest(generateParams.model, Date.now() - startTime);
                return result;
            }
            
            throw new Error(result.error);
            
        } catch (error) {
            logger.warn(`Ollama generate failed for model ${generateParams.model}:`, error.message);
            
            if (this.fallbackEnabled) {
                return await this.handleFallback(generateParams, userId, companyId, 'generate', error);
            }
            
            throw error;
        }
    }

    async handleFallback(params, userId, companyId, action, originalError) {
        try {
            const fallbackModel = await this.selectFallbackModel(params.model, companyId);
            
            if (!fallbackModel) {
                throw new Error(`No fallback available for model ${params.model}`);
            }

            logger.info(`Falling back from Ollama ${params.model} to ${fallbackModel.provider}:${fallbackModel.model}`);

            const fallbackResult = await this.executeFallback(params, fallbackModel, action);
            
            fallbackResult.fellback = true;
            fallbackResult.originalProvider = 'ollama';
            fallbackResult.originalModel = params.model;
            fallbackResult.originalError = originalError.message;
            
            await this.trackFallbackUsage(userId, companyId, params.model, fallbackModel, action);
            
            return fallbackResult;
            
        } catch (fallbackError) {
            logger.error('Fallback also failed:', fallbackError.message);
            throw new Error(`Both Ollama and fallback failed: ${originalError.message}, Fallback: ${fallbackError.message}`);
        }
    }

    async selectFallbackModel(ollamaModel, companyId) {
        const company = await this.getCompanySettings(companyId);
        const fallbackConfig = company?.ollamaSettings?.fallbackConfig;
        
        if (!fallbackConfig?.enabled) {
            return null;
        }

        const modelMapping = this.getModelMapping(ollamaModel);
        
        for (const provider of this.fallbackProviders) {
            if (fallbackConfig.allowedProviders?.includes(provider) && modelMapping[provider]) {
                return {
                    provider,
                    model: modelMapping[provider],
                    apiKey: fallbackConfig[`${provider}ApiKey`]
                };
            }
        }

        return null;
    }

    getModelMapping(ollamaModel) {
        const mappings = {
            'llama3.1:8b': {
                openai: 'gpt-4o-mini',
                anthropic: 'claude-3-haiku-20240307'
            },
            'llama3:8b': {
                openai: 'gpt-4o-mini',
                anthropic: 'claude-3-haiku-20240307'
            },
            'mistral:7b-instruct': {
                openai: 'gpt-4o-mini',
                anthropic: 'claude-3-haiku-20240307'
            },
            'codellama:7b': {
                openai: 'gpt-4o',
                anthropic: 'claude-3-sonnet-20240229'
            }
        };

        const baseModel = ollamaModel.split(':')[0];
        return mappings[ollamaModel] || mappings[baseModel] || {
            openai: 'gpt-4o-mini',
            anthropic: 'claude-3-haiku-20240307'
        };
    }

    async executeFallback(params, fallbackModel, action) {
        switch (fallbackModel.provider) {
            case 'openai':
                return await this.executeOpenAIFallback(params, fallbackModel, action);
            case 'anthropic':
                return await this.executeAnthropicFallback(params, fallbackModel, action);
            default:
                throw new Error(`Unsupported fallback provider: ${fallbackModel.provider}`);
        }
    }

    async executeOpenAIFallback(params, fallbackModel, action) {
        throw new Error('OpenAI fallback not implemented - requires OpenAI service integration');
    }

    async executeAnthropicFallback(params, fallbackModel, action) {
        throw new Error('Anthropic fallback not implemented - requires Anthropic service integration');
    }

    async trackSuccessfulRequest(model, responseTime) {
        logger.info(`Ollama request successful for ${model} in ${responseTime}ms`);
    }

    async trackFallbackUsage(userId, companyId, originalModel, fallbackModel, action) {
        logger.info(`Fallback used: ${originalModel} -> ${fallbackModel.provider}:${fallbackModel.model}`);
        
        await ollamaService.trackUsage(userId, companyId, originalModel, `${action}_fallback`, 0, {
            fallbackProvider: fallbackModel.provider,
            fallbackModel: fallbackModel.model,
            success: true
        });
    }

    async getCompanySettings(companyId) {
        try {
            const { Company } = require('../models');
            return await Company.findById(companyId);
        } catch (error) {
            logger.error('Error getting company settings for fallback:', error);
            return null;
        }
    }

    async configureFallback(companyId, config) {
        try {
            const { Company } = require('../models');
            const company = await Company.findById(companyId);
            
            if (!company) {
                throw new Error('Company not found');
            }

            company.ollamaSettings = {
                ...company.ollamaSettings,
                fallbackConfig: {
                    enabled: config.enabled || false,
                    allowedProviders: config.allowedProviders || [],
                    openaiApiKey: config.openaiApiKey || null,
                    anthropicApiKey: config.anthropicApiKey || null,
                    azureConfig: config.azureConfig || null,
                    priority: config.priority || ['openai', 'anthropic', 'azure']
                }
            };

            await company.save();
            return company.ollamaSettings.fallbackConfig;

        } catch (error) {
            logger.error('Error configuring fallback:', error);
            throw error;
        }
    }
}

module.exports = new OllamaFallbackService();
