const { PAYMENT, EMAIL, SERVER, SUPPORT_EMAIL } = require('../config/config');
/**
 * @type { import('stripe').Stripe }
 */
const stripe = require('stripe')(PAYMENT.STRIPE_SECRET_KEY);
const User = require('../models/user');
const Subscription = require('../models/subscription');
const { SUBSCRIPTION_TYPE, MOMENT_FORMAT, STORAGE_REQUEST_STATUS, EMAIL_TEMPLATE, APPLICATION_ENVIRONMENT } = require('../config/constants/common');
const moment = require('moment-timezone');
const logger = require('../utils/logger');
const { approveStorageRequest, checkStorageRequest } = require('./storageRequest');
const publishSSEEvent = require('../sse/publishSSEEvents');
const { checkSubscription } = require('./auth');
const { getTemplate } = require('../utils/renderTemplate');
const { sendSESMail } = require('./email');
const { timestampToDate, bytesToMegabytes } = require('../utils/helper');
const { INVITATION_TYPE } = require('../config/constants/common');
const Log = require('../models/log');
const { addUserMsgCredit, updateUserMsgCredit } = require('./user');
const company = require('../models/company');
const { createInvoiceFromEvent } = require('./invoice');
const { updateCRMSubscriptionStatus } = require('./freshsales');

const cancelSubscription = async (req) => {
    try { 
        const subscriptionRecord = await checkSubscription(req);

        if (!subscriptionRecord) return false;

        if (subscriptionRecord.status === SUBSCRIPTION_TYPE.PENDING_CANCELLATION) {
            throw new Error(_localize('subscription.alreadyCancel', req, ''));
        }

        const cancelSub = await stripe.subscriptions.update(subscriptionRecord.subscriptionId, {
            cancel_at_period_end: true
        });

        if (!cancelSub) return false;

        // Convert Unix timestamp to formatted date
        const formattedCancelDate = moment.unix(cancelSub.cancel_at).format(MOMENT_FORMAT);
        const [subription, companyRecord] = await Promise.all([
            Subscription.updateOne({ 'company.id': req.user.company.id }, 
                { 
                    $set: {
                        status: SUBSCRIPTION_TYPE.PENDING_CANCELLATION,
                        cancelAt: formattedCancelDate,
                        cancellation_reason: req.body.cancel_reason
                    }
                }),
            company.findById({ _id: req.user.company.id }, { freshCRMContactId: 1 })
        ]);

        const emailData = {
            name: req.user.fname + ' ' + req.user.lname,
            cancellation_date: timestampToDate(cancelSub.cancel_at)
        }   

        getTemplate(EMAIL_TEMPLATE.CANCEL_SUBSCRIPTION, emailData).then(async (template) => {
            await sendSESMail(req.user.email, template.subject, template.body, attachments = [])
        })

        if(SERVER.NODE_ENV === APPLICATION_ENVIRONMENT.PRODUCTION){

            const cancelSubscriptionData = {
                company_name: req?.user?.company?.name,
                email: req?.user?.email,
                country: req?.countryName,
                cancellation_date: timestampToDate(cancelSub.cancel_at),
                cancellation_reason: req.body.cancel_reason
            }
            
            const subscriptionEmail = EMAIL.SUBSCRIPTION_EMAIL.split(',');
            getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_CANCEL_ADMIN, cancelSubscriptionData).then(async (template) => {
                await sendSESMail(SUPPORT_EMAIL, template.subject, template.body, attachments = [],subscriptionEmail)
            })
            updateCRMSubscriptionStatus(companyRecord.freshCRMContactId, 'Weam AI', SUBSCRIPTION_TYPE.CANCEL, req.body.cancel_reason);
        }

        Log.create({
            type: 'subscription-canceled',
            status: 'active',
            data: {
                ...req.body,
                userId: req.userId,
                companyId: req.user.company.id,
                subscriptionId: subscriptionRecord.subscriptionId
            }
        }).catch(err => handleError(err, 'Error logging subscription cancellation'));

        return subription;
    } catch (error) {
        handleError(error, 'Error - cancelSubscription');
    }
}

const createSubscription = async (req, customerId) => {
    try {
        // Prepare subscription data
        const subscriptionData = {
            customer: customerId,
            items: [
                {
                    price: req.body.price_id,
                    quantity: req.body.quantity,
                }
            ],
            payment_settings: {
                payment_method_options: {
                    card: {
                        request_three_d_secure: 'automatic', // Request 3D Secure if supported
                    },
                },
            },            
            expand: ['latest_invoice.payment_intent']
        };

        
        // Validate and add coupon if provided
        if (req.body.coupon) {
            // Verify coupon validity
            const coupon = await stripe.coupons.retrieve(req.body.coupon);
            if (coupon && coupon.valid) {
                subscriptionData.coupon = req.body.coupon;
            } else {
                throw new Error(_localize('subscription.invalidCoupon', req, ''));
            }
        }

        // Create the subscription with the calculated package count
        const subscription = await stripe.subscriptions.create(subscriptionData);

        return subscription;
    } catch (error) {
        handleError(error, 'Error - createSubscription');
    }
}

const createCustomer = async (req) => {
    let customer = null;
    let defaultPaymentMethod = null;
    let subscription = null;

    try {
        const subscriptionRecord = await checkSubscription(req);
        if (subscriptionRecord) {
            throw new Error(_localize('subscription.alreadyExists', req, ''))
        }

        const userCount = await User.countDocuments({ 
            'company.id': req.user.company.id,
            inviteSts: INVITATION_TYPE.ACCEPT
        });

        //Check if the user count is more than the subscription plan
        if(userCount > req.body.quantity) {
            throw new Error(_localize('subscription.userLimitExceeded', req, ''));
        }

        // Step 1: Create Stripe customer
        customer = await stripe.customers.create({
            email: req.user.email,
            name: req.user.company.name,
            payment_method: req.body.payment_method,
        });

        // Step 2: Attach payment method
        defaultPaymentMethod = await stripe.paymentMethods.attach(req.body.payment_method, {
            customer: customer.id,
        });

        // Step 3: Update customer's default payment method
        await stripe.customers.update(customer.id, {
            invoice_settings: {
                default_payment_method: defaultPaymentMethod.id,
            },
        });

        // Step 4: Create subscription
        subscription = await createSubscription(req, customer.id);
        if (!subscription) throw new Error(_localize('subscription.createError', req, ''));

        // Extract payment intent and its status
        const paymentIntent = subscription?.latest_invoice?.payment_intent;
        const paymentStatus = paymentIntent?.status;
        
        if (paymentStatus === 'requires_action' || paymentStatus === 'requires_source_action') {
            return {
                requiresAction: true,
                subscription: {
                    latest_invoice: {
                        payment_intent: {
                            client_secret: paymentIntent.client_secret
                        }
                    },
                    id:subscription.id,
                    current_period_start:subscription.current_period_start,
                    current_period_end: subscription.current_period_end,
                    currency: subscription.currency,
                    plan:{
                        amount: subscription.plan.amount,
                    }
                },
                customer:{
                    id:customer.id
                }
            };
        } else if (paymentStatus !== 'succeeded') {
            throw new Error(_localize('subscription.paymentFailed', req, ''));            
        } 

        const result = await handlePayment3dSecure(req, subscription, customer);
        
        return result;
        
    } catch (error) {
        // Rollback steps in reverse order
        try {
            if (subscription) {
                await stripe.subscriptions.cancel(subscription.id);

                // Rollback subscription record from database
                await Subscription.deleteOne({
                    subscriptionId: subscription.id
                });
            }

            if (defaultPaymentMethod) {
                await stripe.paymentMethods.detach(defaultPaymentMethod.id);
            }

            if (customer) {
                await stripe.customers.del(customer.id);
            }
            
        } catch (rollbackError) {
            handleError(rollbackError, 'Error during rollback in createCustomer');
        }

        handleError(error, 'Error - createCustomer');
    }
}

const upcomingInvoice = async (req) => {
    try {
        const subscriptionRecord = await checkSubscription(req);

        if (!subscriptionRecord) return false;

        const result = await stripe.invoices.retrieveUpcoming({
            customer: subscriptionRecord.customerId,
            subscription: subscriptionRecord.subscriptionId
        });

        if (!result) return false;
        return result;
    } catch (error) {
        handleError(error, 'Error - upcomingInvoice');
    }
}

const fetchProductPrice = async (req) => {
    try {
        const price = await stripe.prices.retrieve(req.params.priceId, {
            expand: ['product']
        });
        const result = {
            // unit: price?.transform_quantity?.divide_by,
            unit:1,
            currency: price.currency,
            unit_amount: price.unit_amount,
            interval: price.recurring ? price.recurring.interval : null,
            product_name: price?.product?.name,
            notes: price?.product?.metadata
        };
        
        return result;
    } catch (error) {
        return { unit_amount: 0 };
    }
}

const fetchStripePlans = async (req) => {
    try {
        // Fetch plans in a single API call using list with price IDs filter
        const plans = await stripe.plans.list({
            ids: [
                process.env.STRIPE_LITE,
                process.env.STRIPE_PRO
            ],
            expand: ['data.product'] // Optional: Include product details if needed
        });

        return plans.data;
    } catch (error) {
        handleError(error, 'Error - fetchStripePlans');
    }
}

const getSubscription = async (req) => {
    try {
        const subscriptionRecord = await checkSubscription(req);

        if (!subscriptionRecord || !subscriptionRecord?.subscriptionId) return false;

        const subscription = await stripe.subscriptions.retrieve(subscriptionRecord?.subscriptionId, {
            expand: ['items.data.price.product']
        });

        const enhancedSubscription = {
            ...subscription, // Spread the original subscription object
            subscriptionStatus: subscriptionRecord.status
        };


        return req.originalUrl.includes('/web/')? {subscriptionStatus:subscriptionRecord.status}  :enhancedSubscription;
    } catch (error) {
        handleError(error, 'Error - fetchSubscription');
    }
}


const updateSubscription = async (req) => {
    try {
        const subscriptionRecord = await checkSubscription(req);

        // Check if subscription record exists and is active
        if (!subscriptionRecord) {
            throw new Error(_localize('subscription.noActiveSubscription', req, ''));
        }

        const userCount = await User.countDocuments({ 
            'company.id': req.user.company.id,
            inviteSts: INVITATION_TYPE.ACCEPT
        });

        //Check if the user count is more than the subscription plan
        if(userCount > req.body.quantity) {
            throw new Error(_localize('subscription.userLimitExceeded', req, ''));
        }

        if (subscriptionRecord.status === SUBSCRIPTION_TYPE.ACTIVE) {
            // Get current subscription from Stripe
            const currentSubscription = await stripe.subscriptions.retrieve(subscriptionRecord.subscriptionId);

            const subscriptionItemId = currentSubscription.items.data[0].id;
            const currentQuantity = currentSubscription.items.data[0].quantity;

            // Determine if this is an upgrade or downgrade by comparing prices
            const isUpgrade = req.body.quantity > currentQuantity;

            // Common subscription update configuration
            const updateConfig = {
                items: [{
                    id: subscriptionItemId,
                    price: req.body.price_id,
                    quantity: req.body.quantity
                }],
                proration_behavior: isUpgrade ? 'create_prorations' : 'none'
            };

            // Add coupon if provided
            if (req.body.coupon) {
                // Validate coupon before applying
                const coupon = await stripe.coupons.retrieve(req.body.coupon);
                if (coupon && coupon.valid) {
                    updateConfig.coupon = req.body.coupon;
                } else {
                    throw new Error(_localize('subscription.invalidCoupon', req, ''));
                }
            }

            // Update subscription in Stripe
            const updatedSubscription = await stripe.subscriptions.update(
                subscriptionRecord.subscriptionId,
                updateConfig
            );
            // Update subscription in database
            await Subscription.updateOne(
                { 'company.id': req.user.company.id },
                {
                    $set: {
                        allowuser: req.body.quantity,
                        coupon: req.body.coupon || null,
                        notes: req?.body?.notes
                    }
                }
            );

            if(req?.body?.notes?.credit != subscriptionRecord?.notes?.credit){
                await updateUserMsgCredit(req.user.company.id, req?.body?.notes?.credit);
            }

            const eventData = {
                type: 'subscription-updated', 
                message: "Subscription has been updated",
                timestamp: new Date(),
                data: {
                    plan: req?.body?.plan_name,
                    status: SUBSCRIPTION_TYPE.ACTIVE,
                    companyId: req.user.company.id,
                },
            };
            await publishSSEEvent(eventData);  
            
            const emailData = {
                name: req.user.fname + ' ' + req.user.lname
            }

            getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_UPDATE, emailData).then(async (template) => {
                await sendSESMail(req.user.email, template.subject, template.body, attachments = [])
            });

            if(SERVER.NODE_ENV === APPLICATION_ENVIRONMENT.PRODUCTION){

                const updateSubscriptionData = {
                    company_name: req?.user?.company?.name,
                    email: req?.user?.email,
                    country: req?.countryName,
                    invoice_id: updatedSubscription.latest_invoice,
                    currency: updatedSubscription.currency,
                    start_date: moment.unix(updatedSubscription.current_period_start).format(MOMENT_FORMAT),
                    end_date: moment.unix(updatedSubscription.current_period_end).format(MOMENT_FORMAT),
                    new_quantity: req?.body?.quantity,
                    old_quantity: currentQuantity,
                    subscription_id: updatedSubscription.id,
                    payment_gateway: 'Stripe'
                }

                const subscriptionEmail = EMAIL.SUBSCRIPTION_EMAIL.split(',');

                getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_UPDATE_ADMIN, updateSubscriptionData).then(async (template) => {
                    await sendSESMail(SUPPORT_EMAIL, template.subject, template.body, attachments = [],subscriptionEmail)
                })
            }

            Log.create({
                type: 'subscription-updated',
                status: 'active',
                data: {
                    ...req.body,
                    userId: req.userId,
                    companyId: req.user.company.id,
                    subscriptionId: subscriptionRecord.subscriptionId,
                    message: "Subscription updated with existing customer"
                }
            }).catch(err => handleError(err, 'Error logging subscription update'));

            return updatedSubscription;
        } else {
            // Create a new subscription if the current one is not active
            const newSubscription = await createSubscription(req, subscriptionRecord.customerId);
            
            // Update subscription in database
            await Subscription.updateOne(
                { 'company.id': req.user.company.id },
                {
                    $set: {
                        allowuser: req.body.quantity,
                        coupon: req.body.coupon || null,
                        subscriptionId: newSubscription.id,
                        status: SUBSCRIPTION_TYPE.ACTIVE,
                        notes: req?.body?.notes
                    }
                }
            );

            addUserMsgCredit(req.user.company.id, req?.body?.notes?.credit);

            const eventData = {
                type: 'subscription-updated', 
                message: "Subscription has been updated",
                timestamp: new Date(),
                data: {
                    plan: req.body.plan_name,
                    status: SUBSCRIPTION_TYPE.ACTIVE,
                    companyId: req.user.company.id,
                },
            };
            await publishSSEEvent(eventData);    

            const emailData = {
                name: req.user.fname + ' ' + req.user.lname
            }
            getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_UPDATE, emailData).then(async (template) => {
                await sendSESMail(req.user.email, template.subject, template.body, attachments = [])
            })

            if(SERVER.NODE_ENV === APPLICATION_ENVIRONMENT.PRODUCTION){

                const updateSubscriptionData = {
                    company_name: req?.user?.company?.name,
                    email: req?.user?.email,
                    country: req?.countryName,
                    invoice_id: newSubscription.latest_invoice,
                    currency: newSubscription.currency,
                    start_date: moment.unix(newSubscription.current_period_start).format(MOMENT_FORMAT),
                    end_date: moment.unix(newSubscription.current_period_end).format(MOMENT_FORMAT),
                    new_quantity: req?.body?.quantity,
                    old_quantity: currentQuantity,
                    subscription_id: newSubscription.id,
                    payment_gateway: 'Stripe',
                }

                const subscriptionEmail = EMAIL.SUBSCRIPTION_EMAIL.split(',');
                getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_UPDATE_ADMIN, updateSubscriptionData).then(async (template) => {
                    await sendSESMail(SUPPORT_EMAIL, template.subject, template.body, attachments = [],subscriptionEmail)
                    })
            }

            Log.create({
                type: 'subscription-updated',
                status: 'active',
                data: {
                    ...req.body,
                    userId: req.userId,
                    companyId: req.user.company.id,
                    subscriptionId: newSubscription.id,
                    message: "Subscription created with existing customer"
                }
            }).catch(err => handleError(err, 'Error logging subscription update'));

            return newSubscription;
        }
        
    } catch (error) {
        handleError(error, 'Error - updateSubscription');
    }
}

const updatePaymentMethod = async (req, res) => {
    try {
        const subscriptionRecord = await checkSubscription(req);

         // Check if subscription record exists and is active
         if (!subscriptionRecord) {
            throw new Error(_localize('subscription.noSubscription', req, ''));
        }

        const { paymentMethodId } = req.body;
        const customerId = subscriptionRecord?.customerId;

        // 1. Attach the new payment method to the customer
        const attachPromise = stripe.paymentMethods.attach(paymentMethodId, {
            customer: customerId,
        });

        // 2. Retrieve all existing payment methods
        const listPromise = stripe.paymentMethods.list({
            customer: customerId,
            type: 'card',
        });

        const [, paymentMethods] = await Promise.all([
            attachPromise,
            listPromise
        ]);

        // 3. Set the new payment method as default
        await stripe.customers.update(customerId, {
            invoice_settings: {
                default_payment_method: paymentMethodId,
            },
        });

        // 4. Remove all old payment methods
        const detachPromises = paymentMethods.data
            .filter(pm => pm.id !== paymentMethodId)
            .map(pm => stripe.paymentMethods.detach(pm.id));
        
        await Promise.all(detachPromises);

        Log.create({
            type: 'payment-method-updated',
            status: 'active',
            data: {
                ...req.body,
                userId: req.userId,
                companyId: req.user.company.id,
                customerId: subscriptionRecord.customerId
            }
        }).catch(err => handleError(err, 'Error logging payment method update'));

        return true;
    } catch (error) {
        handleError(error, 'Error updating payment method');
        throw error;
    }
}

const defaultPaymentMethod = async (req) => {
    try {
        const subscriptionRecord = await checkSubscription(req);

        if (!subscriptionRecord) {
            throw new Error(_localize('subscription.noSubscription', req, ''));
        }

        // Get customer's default payment method
        const customer = await stripe.customers.retrieve(subscriptionRecord.customerId, {
            expand: ['invoice_settings.default_payment_method']
        });

        const defaultPaymentMethod = customer.invoice_settings.default_payment_method;

        if (!defaultPaymentMethod) {
            return null;
        }

        // Format the response
        return {
            id: defaultPaymentMethod.id,
            brand: defaultPaymentMethod.card.brand,
            last4: defaultPaymentMethod.card.last4,
            // expMonth: defaultPaymentMethod.card.exp_month,
            // expYear: defaultPaymentMethod.card.exp_year
        };
    } catch (error) {
        handleError(error, 'Error - getDefaultPaymentMethod');
        throw error;
    }
}

const cancelSubscriptionWebhook = async (req) => {
    logger.info('Cancel subscription webhook started');

    const event = req.body;

    if (event.type === 'customer.subscription.deleted') {
        let subscriptionId = event.data.object.id;
        let customerId = event.data.object.customer;

        logger.info('customer.subscription.deleted', subscriptionId);
        logger.info('customer.subscription.deleted data', event);
        
        try {
            // Update the subscription status in your database
           const subscriptionData = await Subscription.findOneAndUpdate(
                { subscriptionId: subscriptionId, customerId: customerId },
                { $set: { status: SUBSCRIPTION_TYPE.CANCEL } },
                { new: true }
            );

             // Prepare event data
            const eventData = {
                type: 'subscription-canceled', 
                message: "Subscription has been canceled",
                timestamp: new Date(),
                data: {
                    status: SUBSCRIPTION_TYPE.CANCEL,
                    companyId: subscriptionData.company.id,
                },
            };

            // Publish the event to Redis Pub/Sub
            await publishSSEEvent(eventData);

            // Respond with a 200 status to acknowledge receipt of the event
            return true;
        } catch (error) {
            handleError(error, 'Error - cancel subscription webhook error');
            throw error;
        }
    }

    logger.info('Cancel subscription webhook completed');
    return true;
}

const invoicePaidWebhook = async (req) => {
    logger.info('Invoice paid webhook started');
    const event = req.body;
    logger.info(`invoice webhook event ${JSON.stringify(event,null,2)}`);
    
    switch (event.type) {
        case 'invoice.paid': {
            logger.info('invoice.paid started to add to database');
            const user_compnay = await User.findOne(
                { email: event?.data?.object?.customer_email }, 
                { company: 1 }
            );
            await createInvoiceFromEvent(event, user_compnay);
            logger.info('invoice.paid data added to database');
            break;
        }

        case 'invoice.payment_succeeded': {
            const invoice = event.data.object;
            logger.info('invoice.payment_succeeded webhook started');
            logger.info(`invoice.payment_succeeded invoice ${JSON.stringify(invoice,null,2)}`);

            if (invoice.billing_reason === 'subscription_renewal' || 
                invoice.billing_reason === 'subscription_cycle') {
                const subscriptionId = invoice.subscription;
                const stripeSubscription = await stripe.subscriptions.retrieve(subscriptionId);
                logger.info(`invoice.payment_succeeded subscriptionId ${subscriptionId}`);
                logger.info(`invoice.payment_succeeded stripeSubscription ${JSON.stringify(stripeSubscription,null,2)}`);
                
                // Format dates using moment
                const startDate = moment.unix(stripeSubscription.current_period_start).format(MOMENT_FORMAT);
                const endDate = moment.unix(stripeSubscription.current_period_end).format(MOMENT_FORMAT);
                
                logger.info(`invoice.payment_succeeded startDate ${startDate}`);
                logger.info(`invoice.payment_succeeded endDate ${endDate}`);
                // Update subscription date in database
                const subscription = await Subscription.findOneAndUpdate(
                    { subscriptionId: subscriptionId },
                    { 
                        $set: {
                            startDate,
                            endDate,
                            notes: {
                                
                                credit: stripeSubscription.plan?.metadata?.credit || 0,
                                plan_name: stripeSubscription.plan?.metadata?.plan_name || '',
                                plan_code: stripeSubscription.plan?.metadata?.plan_code || ''
                            }
                        }
                    },
                    { new: true }
                );
                logger.info(`invoice.payment_succeeded subscription ${JSON.stringify(subscription,null,2)}`);
                
                logger.info(`invoice.payment_succeeded subscription ${JSON.stringify(stripeSubscription,null,2)}`);
                logger.info(`invoice.payment_succeeded subscription notes ${JSON.stringify(stripeSubscription?.metadata,null,2)}`);
                if (subscription?.company?.id) {
                    await addUserMsgCredit(subscription.company.id, subscription?.notes?.credit);
                }

                //OPTIMIZE: do this in a single query
                //Get the active users count
                const activeUsersCount = await User.countDocuments({
                    'company.id': subscription.company.id,
                    inviteSts: INVITATION_TYPE.ACCEPT
                });

                //Get the pending removal users count
                const pendingRemovalUsersCount = await User.countDocuments({
                    'company.id': subscription.company.id,
                    inviteSts: INVITATION_TYPE.PENDING_REMOVAL
                });

                //Pending removal users count is greater than 0
                if(pendingRemovalUsersCount > 0){
                    await stripe.subscriptions.update(subscriptionId, {
                        quantity: activeUsersCount
                    });
                    
                    // Update subscription in database
                    const subscription = await Subscription.findOneAndUpdate(
                        { subscriptionId: subscriptionId },
                        { 
                            $set: {
                                allowuser: activeUsersCount
                            }
                        },
                        { new: true }
                    );
                    
                    // write a query to hard delete the user from user collection whose status is pending_removal
                    await User.deleteMany({
                        'company.id': subscription.company.id,
                        inviteSts: INVITATION_TYPE.PENDING_REMOVAL
                    });
                }

                logger.info('Subscription updated with new period dates');
            }
            break;
        }
    }

    logger.info('Invoice paid webhook completed');
    return true;
}

const getInvoiceList = async (req) => {
    try {
        const { startingAfter, limit = 50 } = req.body;

        const subscriptionRecord = await checkSubscription(req);

        // Check if subscription record exists and is active
        if (!subscriptionRecord) {
            return true;
        }

        // Fetch the invoices from Stripe
        const invoices = await stripe.invoices.list({
            customer: subscriptionRecord?.customerId,
            limit: parseInt(limit),
            starting_after: startingAfter || undefined,
        });

        const data = {
            records: invoices.data,
            has_more: invoices.has_more,
            next_starting_after: invoices.has_more ? invoices.data[invoices.data.length - 1].id : null,
        };

        return data;
    } catch (error) {
        handleError(error, 'Error - Invoice list fetch error');
        throw error;
    }
}

const storageRequestCharge = async (req) => {
    try {

        const [storageRequest, subscriptionRecord] = await Promise.all([
            checkStorageRequest(req.body.storageRequestId, STORAGE_REQUEST_STATUS.PENDING, req.user.company.id),
            checkSubscription(req)
        ]);

        if (!storageRequest) {
            throw new Error(_localize('module.invalid', req, 'Storage Request'));
        }

        if (!subscriptionRecord) {
            throw new Error(_localize('subscription.noSubscription', req, ''));
        }

        // Get the customer's default payment method
        const customer = await stripe.customers.retrieve(subscriptionRecord.customerId, {
            expand: ['invoice_settings.default_payment_method']
        });
        
        const paymentIntent = await stripe.paymentIntents.create({
            amount: Math.round(req.body.amount),
            currency: req.body.currency.toLowerCase(),
            customer: subscriptionRecord.customerId,
            description: 'Charge for storage request (' + req.body.storageRequestId + ')',
            metadata: {
              'Storage Request Id': req.body.storageRequestId,
              'Requested Storage Size': storageRequest?.requestSize,
              'Updated Storage Size': req?.body?.updatedStorageSize
            },
            payment_method: customer.invoice_settings.default_payment_method?.id,
            setup_future_usage: 'off_session', // This helps with future off-session payments
        });
        
        // Return the client secret so that the client can handle authentication if needed
        return {
            requires_action: true,
            payment_intent_client_secret: paymentIntent.client_secret,
            storageRequestId: req.body.storageRequestId,
            updatedStorageSize: req.body.updatedStorageSize
        };
    } catch (error) {
        handleError(error, 'Error - storageRequestCharge');
        throw error;
    }
};

const confirmStorageCharge = async (req) => {
    try {
        const { paymentIntentId, storageRequestId, updatedStorageSize, priceId } = req.body;
        
        const paymentIntent = await stripe.paymentIntents.retrieve(paymentIntentId);
        
        if (paymentIntent.status === 'succeeded') {
            // Run these queries in parallel since they don't depend on each other
            const [storageRequest, subscriptionRecord] = await Promise.all([
                checkStorageRequest(storageRequestId, STORAGE_REQUEST_STATUS.PENDING, req.user.company.id),
                checkSubscription(req)
            ]);
            
            if (!storageRequest) {
                throw new Error(_localize('module.invalid', req, 'Storage Request'));
            }

            if (!subscriptionRecord) {
                throw new Error(_localize('subscription.noSubscription', req, ''));
            }
            
            await approveStorageRequest(storageRequestId, updatedStorageSize);
            
            try {
                  
            // Create invoice
            const stripeInvoice = await stripe.invoices.create({
                customer: subscriptionRecord.customerId,
                auto_advance: false,
                collection_method: 'charge_automatically',
                metadata: {
                    'Storage Request Id': storageRequestId,
                    'PaymentIntent Id': paymentIntentId
                }
            });
            
            // Create invoice item
            await stripe.invoiceItems.create({
                customer: subscriptionRecord.customerId,
                invoice: stripeInvoice.id,
                amount: paymentIntent.amount,
                currency: paymentIntent.currency,
                description: `Storage upgrade to ${bytesToMegabytes(updatedStorageSize)} MB`,
            });
            
            // The finalize and pay operations must happen sequentially
            const finalizedInvoice = await stripe.invoices.finalizeInvoice(stripeInvoice.id, {
                auto_advance: false
            });
            
            // Mark the invoice as paid
            const paidInvoice = await stripe.invoices.pay(finalizedInvoice.id, {
                paid_out_of_band: true
            });

                
                logger.info('Created and paid storage upgrade invoice:', paidInvoice.id);
                
                // Update the log with invoice information
                Log.create({
                    type: 'storage-request-charge',
                    status: 'active',
                    data: {
                        ...req.body,
                        userId: req.userId,
                        companyId: req.user.company.id,
                        storageRequestId: storageRequestId,
                        invoiceId: paidInvoice.id,
                        amount: paymentIntent.amount
                    }
                }).catch(err => handleError(err, 'Error logging storage charge'));
                
            } catch (invoiceError) {
                // Log but don't fail the entire operation if invoice creation fails
                logger.error('Error creating invoice for storage charge:', invoiceError);
                
                // Still create a log entry even if invoice creation fails
                Log.create({
                    type: 'storage-request-charge',
                    status: 'active',
                    data: {
                        ...req.body,
                        userId: req.userId,
                        companyId: req.user.company.id,
                        storageRequestId: storageRequestId,
                        invoiceError: invoiceError.message
                    }
                }).catch(err => handleError(err, 'Error logging storage charge'));
            }
            
            return { success: true };
        } else if (paymentIntent.status === 'requires_action' || 
                   paymentIntent.status === 'requires_confirmation') {
            // Still needs authentication or confirmation
            return {
                requires_action: true,
                payment_intent_client_secret: paymentIntent.client_secret
            };
        } else {
            // Handle any other payment status as failed
            throw new Error(`Payment failed with status: ${paymentIntent.status}`);
        }
    } catch (error) {
        handleError(error, 'Error - confirmStorageCharge');
        throw error;
    }
};

const checkCoupon = async (req) => {
    try {
        const coupon = await stripe.coupons.retrieve(req.body.coupon);
        if (coupon && coupon.valid) {
            return coupon;
        } else { 
            return { valid: false, message: _localize('subscription.invalidCoupon', req, '') };
        }
    } catch (error) {
        handleError(error, 'Error - validateCoupon');
        throw error;
    }
}

const uncancelSubscription = async (req) => {
    try {
        const subscriptionRecord = await checkSubscription(req);

        if (!subscriptionRecord) {
            throw new Error(_localize('module.notFound', req, 'Subscription'));
        }
        const updatedSubscription = await stripe.subscriptions.update(subscriptionRecord?.subscriptionId, {
            cancel_at_period_end: false,
        });

        await Subscription.updateOne(
            { 'company.id': req.user.company.id },
            {
              $set: {
                status: SUBSCRIPTION_TYPE.ACTIVE
              },
              $unset: {
                cancelAt: "", 
                cancellation_reason: ""
              }
            }
        );

        const emailData = {
            name: req.user.fname + ' ' + req.user.lname            
        }   

        getTemplate(EMAIL_TEMPLATE.UN_CANCEL_SUBSCRIPTION, emailData).then(async (template) => {
            await sendSESMail(req.user.email, template.subject, template.body, attachments = [])
        })

        Log.create({
            type: 'subscription-uncanceled',
            status: 'active',
            data: {
                ...req.body,
                userId: req.userId,
                companyId: req.user.company.id,
                subscriptionId: subscriptionRecord.subscriptionId
            }
        }).catch(err => handleError(err, 'Error logging subscription uncancellation'));
        
        return updatedSubscription;
    } catch (error) {
        console.error('Error uncancelling subscription:', error);
        throw error;
    }
}

const handlePayment3dSecure = async (req, subscriptionParam, customerParam)=>{
    try{
        // const {subscription,customer} = req.body
        const subscription = subscriptionParam || req.body.subscription;
        const customer = customerParam || req.body.customer;
        
        const startDate = moment.unix(subscription.current_period_start).format(MOMENT_FORMAT);
        const endDate = moment.unix(subscription.current_period_end).format(MOMENT_FORMAT);

        // Step 5: Create subscription record
        const subscriptiondata = await Subscription.create({
            status: SUBSCRIPTION_TYPE.ACTIVE,
            plan: req.body.price_id,
            planName: req.body.plan_name,
            gateway: 'stripe',
            allowuser: req.body.quantity,
            startDate,
            endDate,
            company: req.user.company,
            subscriptionId: subscription.id,
            notes: req?.body?.notes,
            customerId: customer.id,
            createdBy: req.user._id,
            updatedBy: req.user._id
        });

        const [_, companyRecord] = await Promise.all([
            company.updateOne(
                { _id: req.user.company.id }, 
                { $unset: { freeCredit: '', freeTrialStartDate: '' }}
            ),
            company.findById({ _id: req.user.company.id }, { freshCRMContactId: 1 })
        ]);
        
        // Update credit for all users in the same company
        addUserMsgCredit(req.user.company.id, req?.body?.notes?.credit);  

        // Prepare event data
         const eventData = {
            type: 'subscription-created', 
            message: "Subscription has been created",
            timestamp: new Date(),
            data: {
                plan: req.body.plan_name,
                startDate,
                status: SUBSCRIPTION_TYPE.ACTIVE,
                allowedUsers: req.body.quantity,
                createdBy: {
                    id: req.user._id,
                    email: req.user.email,
                },
                companyId: req.user.company.id,
            },
        };

        const emailData = {
            name: req.user.fname + ' ' + req.user.lname
        }

        getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_PURCHASE, emailData).then(async (template) => {
            await sendSESMail(req.user.email, template.subject, template.body, attachments = [])
        })

        if(SERVER.NODE_ENV === APPLICATION_ENVIRONMENT.PRODUCTION){

            const purchaseAdminData = {
                company_name: req?.user?.company?.name,
                email: req?.user?.email,
                country: req?.countryName,
                amount: (Number(subscription.plan.amount)/100 * Number(req?.body?.quantity)),
                currency: subscription.currency,
                start_date: startDate,
                end_date: endDate,
                number_of_users: req?.body?.quantity,
            }

            const subscriptionEmail = EMAIL.SUBSCRIPTION_EMAIL.split(',');
            getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_PURCHASE_ADMIN, purchaseAdminData).then(async (template) => {
                await sendSESMail(SUPPORT_EMAIL, template.subject, template.body, attachments = [],subscriptionEmail)
            })
            updateCRMSubscriptionStatus(companyRecord.freshCRMContactId, req.body.plan_name, SUBSCRIPTION_TYPE.ACTIVE);
        }


         Log.create({
            type: 'subscription-created',
            status: 'active',
            data: {
                ...req.body,
                userId: req.userId,
                companyId: req.user.company.id,
                subscriptionId: subscriptiondata.subscriptionId
            }
        }).catch(err => handleError(err, 'Error logging subscription created'));

        // Publish the event to Redis Pub/Sub
        await publishSSEEvent(eventData);

        return subscription;

    }catch(error){
        handleError(error, 'Error - handlePayment3dSecure');
    } 
}

module.exports = {
    createCustomer,
    cancelSubscription,
    upcomingInvoice,
    fetchProductPrice,
    getSubscription,
    updateSubscription,
    updatePaymentMethod,
    defaultPaymentMethod,
    cancelSubscriptionWebhook,
    getInvoiceList,
    storageRequestCharge,
    confirmStorageCharge,
    invoicePaidWebhook,
    checkCoupon,
    uncancelSubscription,
    handlePayment3dSecure,
    fetchStripePlans
}