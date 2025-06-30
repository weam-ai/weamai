const Razorpay = require("razorpay");
const { checkSubscription } = require("./auth");
const User = require("../models/user");
const Subscription = require("../models/subscription");
const { INVITATION_TYPE, RAZORPAY_SUBSCRIPTION_TYPE, STORAGE_REQUEST_STATUS, RAZORPAY_PLAN_AMOUNT } = require("../config/constants/common");
const { RAZORPAY } = require("../config/config");
const { getCompanyId, timestampToDate } = require("../utils/helper");
const crypto = require("crypto");
const { SUBSCRIPTION_TYPE } = require("../config/constants/common");
const { getTemplate } = require("../utils/renderTemplate");
const { EMAIL_TEMPLATE,MOMENT_FORMAT } = require("../config/constants/common");
const  Log  = require("../models/log");
const { sendSESMail } = require("./email");
const moment = require("moment");
const company = require('../models/company');
const { addUserMsgCredit, updateUserMsgCredit } = require('./user');
const Invoice = require("../models/invoice");
const dbService = require('../utils/dbService');
const { checkStorageRequest, approveStorageRequest } = require("./storageRequest");

const razorpay = new Razorpay({
    key_id: RAZORPAY.KEY_ID,
    key_secret: RAZORPAY.KEY_SECRET,
});

const verifySubscriptionPayment = async (req) => {
    try {
        const {
            razorpay_payment_id,
            razorpay_subscription_id,
            razorpay_order_id,
            razorpay_signature,
            planId,
            quantity,
            type,
            notes: newPlanNotes
        } = req.body;

        // Verify signature based on payment type
        const hmac = crypto.createHmac('sha256', RAZORPAY.KEY_SECRET);
        if (type === 'subscription') {
            hmac.update(`${razorpay_payment_id}|${razorpay_subscription_id}`);
        } else if (type === 'order') {
            hmac.update(`${razorpay_order_id}|${razorpay_payment_id}`);
        }
        const generatedSignature = hmac.digest('hex');

        if (generatedSignature !== razorpay_signature) {
            throw new Error(_localize('subscription.invalidSignature', req, ''));
        }

        const subscriptionRecord = await checkSubscription(req);

        // Fetch subscription details
        const razorpaySubscription = await razorpay.subscriptions.fetch(
            razorpay_subscription_id 
        );

        const plan = await razorpay.plans.fetch(razorpaySubscription.plan_id);
        // Update subscription in Razorpay if it's an update operation
        let updatedSubscription = razorpaySubscription;
        if (type === 'order') {
            updatedSubscription = await razorpay.subscriptions.update(
                razorpay_subscription_id,
                {
                    plan_id: planId,
                    quantity: quantity
                }
            );            
        }

        const startDate = moment.unix(Date.now()/1000).format(MOMENT_FORMAT);
        const endDate = moment.unix(Date.now()/1000).add(30, 'days').format(MOMENT_FORMAT);
        // Create or update subscription in DB
        const subscription = await Subscription.findOneAndUpdate(
            {
                subscriptionId: razorpay_subscription_id,
                'company.id': req.user.company.id,
            },
            {
                $set: {
                    gateway: 'razorpay',
                    status:SUBSCRIPTION_TYPE.ACTIVE,
                    customerId: updatedSubscription.customer_id,
                    subscriptionId: razorpay_subscription_id,
                    plan: type === 'order' ? updatedSubscription.plan_id : planId,
                    company: req.user.company,
                    planName: plan.item.name,
                    allowuser: type === 'order' ? updatedSubscription.quantity : quantity,
                    startDate,
                    endDate,
                    lastPaymentId: razorpay_payment_id,
                    createdBy: req.user._id,
                    updatedBy: req.user._id,
                    notes: newPlanNotes,
                    // lastPaymentDate: new Date()
                }
            },
            {
                new: true,
                upsert: true
            }
        );
 
        //4. update user msg credit
        if (type === 'order') {
            if(newPlanNotes?.credit != subscriptionRecord?.notes?.credit){
                await updateUserMsgCredit(req.user.company.id, newPlanNotes?.credit);
            }
        } else {
            await addUserMsgCredit(req.user.company.id, newPlanNotes?.credit);
        }
        
        // Log the transaction
        await Log.create({
            type: type === 'subscription' ? 'subscription-created' : 'subscription-updated',
            status: 'success',
            data: {
                subscriptionId: subscription.subscriptionId,
                paymentId: razorpay_payment_id,
                orderId: razorpay_order_id,
                quantity: subscription.allowuser,
                userId: req.user._id,
                companyId: req.user.company.id
            }
        });

        // Send email notification
        const emailData = {
            name: req.user.fname + ' ' + req.user.lname,
            planDetails: type === 'subscription' 
                ? `New subscription with ${subscription.allowuser} users`
                : `Updated to ${quantity} users`
        };

        getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_UPDATE, emailData).then(async (template) => {
            await sendSESMail(
                req.user.email,
                template.subject,
                template.body,
                []
            );
        });

        return {
            success: true,
            subscription,
            message: type === 'subscription' 
                ? 'Subscription created successfully' 
                : 'Subscription updated successfully'
        };

    } catch (error) {
        handleError(error, `Error - verifyRazorpayPayment`);
        throw error;
    }
};

const createRazorpayOrder = async (amount,currency,notes,token,customerId) => {
    try {

        const options = {
            amount: amount, // Amount in paise 
            receipt: `receipt_${Date.now()}`,
            payment_capture: 1,
            customer_id: customerId,
            notes,
            token,
            currency
        };

        const order = await razorpay.orders.create(options);
        return order;
    } catch (error) {
        console.log("🚀 ~ createRazorpayOrder ~ error:", JSON.stringify(error, null, 2))
        handleError(error, "Error - createRazorpayOrder");
    }
};

const createRazorpaySubscription = async (req, customerId) => {
    try {
        // Prepare subscription data
        const subscriptionData = {
            plan_id: req.body.plan_id,
            customer_notify: 1,
            customer_id: customerId,
            quantity: req.body.quantity,
            total_count: 999,
            notes: req.body.notes
        };

        // Only add offer_id if a coupon is provided
        if (req.body.coupon) {
            subscriptionData.offer_id = req.body.coupon;
        }

        // Create the subscription with the calculated package count
        const subscription = await razorpay.subscriptions.create(subscriptionData);
        
        await company.updateOne(
            { _id: req.user.company.id }, 
            { $unset: { freeCredit: "", freeTrialStartDate: "" }}
        );

        return subscription;

    } catch (error) {
        if (error.statusCode === 400 ) {
            console.error('error.error?.description', error.error?.description)
           handleError(error.error?.description, "Error - createRazorpaySubscription");
        }
        handleError(error, "Error - createRazorpaySubscription");
    }
};

const createSubscription = async (req) => {

    let customer = null;
    let subscription = null;
    try {
        const subscriptionRecord = await checkSubscription(req);
        if (subscriptionRecord) {
            throw new Error(_localize("subscription.alreadyExists", req, ""));
        }

        const userCount = await User.countDocuments({
            "company.id": req.user.company.id,
            inviteSts: INVITATION_TYPE.ACCEPT,
        });

        //Check if the user count is more than the subscription plan
        if (userCount > req.body.quantity) {
            throw new Error(
                _localize("subscription.userLimitExceeded", req, "")
            );
        }

   
        // TODO: refactor this code
        // Step 1: Fetch all Razorpay customers
        const existingCustomers = await razorpay.customers.all();

        // Step 2: Check if the email already exists
        const matchingCustomer = existingCustomers.items.find(
            (customer) => customer.email === req.user.email
        );

        let customerId;
        if (matchingCustomer) {
            // Use the existing customer ID
            customerId = matchingCustomer.id;
        } else {
            // Step 3: Create a new Razorpay customer
            customer = await razorpay.customers.create({
                email: req.user.email,
                name: req.user.fname + " " + req.user.lname,
                contact: req.user.contact, // Optional: add contact info if available
            });
            customerId = customer.id;
        }
    
        // Step 4: Create subscription
        subscription = await createRazorpaySubscription(req, customerId);
        if (!subscription)
            throw new Error(_localize("subscription.createError", req, ""));

        return subscription;
    } catch (error) {
        handleError(error, "Error - createSubscription-Razorpay");
    }
};

const updateSubscriptionInDb = async (req,type, subscription) => {
    try {

        const razorpaySubscription= subscription.payload.subscription.entity;
        const subscriptionRecord = await Subscription.findOne({ "customerId": razorpaySubscription.customer_id });
        if(type === "subscription.cancelled"){
            // if uncanceled not null, then update the subscription in db and create new subscription in razorpay

            const newSubscriptionData = {
                plan_id: razorpaySubscription.plan_id,
                customer_id: razorpaySubscription.customer_id,
                quantity: razorpaySubscription.quantity,
                total_count: razorpaySubscription.total_count,
                customer_notify: 1,
                notes: {
                    ...(subscriptionRecord?.notes && subscriptionRecord.notes)
                },
            }
            
            if(subscriptionRecord?.unCancelAt){
                await unCancelCreateSubscription(newSubscriptionData);
                return true;
            }
        }else if(type === "subscription.charged"){

            if(subscription?.payload?.subscription?.entity?.notes?.credit){
                await addUserMsgCredit(subscriptionRecord?.company?.id, subscription?.payload?.subscription?.entity?.notes?.credit);
            }
        }

        await Subscription.updateOne(
            { subscriptionId: subscription.payload.subscription.entity.id },
            {
                $set: {
                    status: subscription.payload.subscription.entity.status.toUpperCase(),
                    startDate: moment.unix(subscription.payload.subscription.entity.start_at).format(MOMENT_FORMAT),
                    endDate: moment.unix(subscription.payload.subscription.entity.current_end).format(MOMENT_FORMAT),
                    paymentMethod: subscription.payload.subscription.entity.payment_method,
                    plan: subscription.payload.subscription.entity.plan_id,
                    planName: subscription.payload.subscription.entity.notes?.plan_name || subscription.payload.subscription.entity.notes?.plan_code,
                    allowuser: subscription.payload.subscription.entity.quantity,
                    ...(type === "subscription.charged" && {vacantUser: 0})
                }
            }
        );

        return true;
        
    } catch (error) {
        handleError(error, "Error - changeSubscription-Razorpay");
    }
}

const fetchSubscriptionPlan = async (req) => {
    try {
        const subscriptionPlan = {entity: "Plan", count: 0, items: []};

        // const plansArray = [RAZORPAY.PRO_PLAN_ID,RAZORPAY.LITE_PLAN_ID];
        const plansArray = [RAZORPAY.LITE_PLAN_ID];
        for(const planId of plansArray){
            const plan = await razorpay.plans.fetch(planId);
            subscriptionPlan.items.push(plan);
            subscriptionPlan.count++;
        }

        return subscriptionPlan;
    } catch (error) {
        handleError(error, "Error - fetchSubscriptionPlan-Razorpay");
    }
};

const getRazorpaySubscription = async (req) => {
    try {
        const subscriptionRecord = await checkSubscription(req);
       
        if (!subscriptionRecord || !subscriptionRecord?.subscriptionId)
            return false;

        const subscription = await razorpay.subscriptions.fetch(
            subscriptionRecord?.subscriptionId
        );
        const plan = await razorpay.plans.fetch(subscription.plan_id);
        let paymentDetails = null;
        if(subscription.payment_method === "card"){
            paymentDetails= await razorpay.payments.fetchCardDetails(subscriptionRecord.lastPaymentId)
        }else if(subscription.payment_method === "upi"){
            paymentDetails= await razorpay.payments.fetch(subscriptionRecord.lastPaymentId)
        }
        const enhancedSubscription = {
            ...subscription, // Spread the original subscription object
            planName: subscriptionRecord.planName,
            planAmount: plan.item.unit_amount,
            planCurrency: plan.item.currency,
            subscriptionStatus: subscriptionRecord.status,
            paymentDetails,
            paymentMethod: subscription.payment_method
        };

        return req.originalUrl.includes("/web/")
            ? { subscriptionStatus: subscriptionRecord.status }
            : enhancedSubscription;
    } catch (error) {
        handleError(error, "Error - fetchSubscription");
    }
};

const updatePaymentMethod = async (req) => {
    try {
      
        const subscriptionRecord = await checkSubscription(req);

        if(subscriptionRecord){
          
            const [updatedSubscription, log] = await Promise.all([
                Subscription.updateOne(
                    { subscriptionId: subscriptionRecord.subscriptionId },
                    { $set: { paymentMethod: req.body.payment_method } }
                ),
                Log.create({
                    type: 'payment-method-updated',
                    status: 'active',
                    data: {
                        ...req.body,
                        userId: req.userId,
                        companyId: req.user.company.id,
                        customerId: subscriptionRecord.customerId,
                        subscriptionId: subscriptionRecord.subscriptionId,
                        gateway: 'razorpay',
                        message: 'Payment method updated',
                        paymentMethod: req.body.payment_method
                    }
                })
            ]);
        }
        return true;
    } catch (error) {
        handleError(error, 'Error updating payment method');
        throw error;
    }
}

const updateSubscription = async (req) => {
    try {
        //new update data from frontend
        const { coupon, planId,planName, quantity,planAmount, notes: newPlanNotes } = req.body;

        const subscriptionRecord = await checkSubscription(req);
        if (!subscriptionRecord) {
            throw new Error(
                _localize("subscription.noActiveSubscription", req, "")
            );
        }

        const userCount = await User.countDocuments({
            "company.id": req.user.company.id,
            inviteSts: INVITATION_TYPE.ACCEPT,
        });
        //Check if the user count is more than the subscription plan
        if (userCount > quantity) {
            throw new Error(
                _localize("subscription.userLimitExceeded", req, "")
            );
        }

        const olderQuantity = subscriptionRecord.allowuser;
        const newQuantity = quantity;
        let scheduleChangeAt = null;

        if(newQuantity > olderQuantity){
            scheduleChangeAt = 'now';
        }else{
            scheduleChangeAt = 'cycle_end';
        }
       
        
        if (subscriptionRecord.status == SUBSCRIPTION_TYPE.ACTIVE) {
          const currentSubscription = await razorpay.subscriptions.fetch(
            subscriptionRecord.subscriptionId
          );
       
          const updateConfig = {
            plan_id: planId,
            quantity,
            schedule_change_at: scheduleChangeAt,
          };

          if (coupon) {
              updateConfig.offer_id = coupon;
          }
          // 2. Update subscription in Razorpay
          const updatedSubscription = await razorpay.subscriptions.update(
            currentSubscription.id,
            updateConfig
          );
          // 3. Update subscription in our DB
           Subscription.updateOne(
            { "company.id": req.user.company.id },
            {
              $set: {
                plan: planId,
                planName: planName,
                allowuser: quantity,
                coupon: coupon || null,
                notes: newPlanNotes,
              },
            }
          );

          //4. update user msg credit
          if (newPlanNotes?.credit > subscriptionRecord?.notes?.credit) {
            await updateUserMsgCredit(
              req.user.company.id,
              newPlanNotes?.credit
            );

            Log.create({
                type: 'subscription-updated-credit',
                status: 'active',
                data: {
                  ...req.body,
                  userId: req.userId,
                  companyId: req.user.company.id,
                  subscriptionId: subscriptionRecord.subscriptionId,
                  gateway: 'razorpay',
                  message: 'Subscription updated credit',
                  notes: newPlanNotes,
                }
              })
          }

          const emailData = {
            name: req.user.fname + " " + req.user.lname,
          };

          getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_UPDATE, emailData).then(
            async (template) => {
              await sendSESMail(
                req.user.email,
                template.subject,
                template.body,
                (attachments = [])
              );
            }
          );

         
            Log.create({
                type: "subscription-updated",
                status: "active",
                data: {
                    ...req.body,
                    userId: req.userId,
                    companyId: req.user.company.id,
                    subscriptionId: subscriptionRecord.subscriptionId,
                    gateway: "razorpay",
                    message: "Subscription updated",
                    notes: newPlanNotes,
                }
            })
        

          // 5. Return updated subscription
          return { needsPayment: false, updatedSubscription };
        } else {
          // Create a new subscription if the current one is not active
          const newSubscription = await createRazorpaySubscription(
            req,
            subscriptionRecord.customerId
          );

          // Update subscription in database
          await Subscription.updateOne(
            { "company.id": req.user.company.id },
            {
              $set: {
                allowuser: quantity,
                coupon: coupon || null,
                subscriptionId: newSubscription.id,
                status: SUBSCRIPTION_TYPE.ACTIVE,
                notes: newPlanNotes,
              },
            }
          );

          //Add user msg credit
          await addUserMsgCredit(req.user.company.id, newPlanNotes?.credit);

          const emailData = {
            name: req.user.fname + " " + req.user.lname,
          };
          getTemplate(EMAIL_TEMPLATE.SUBSCRIPTION_UPDATE, emailData).then(
            async (template) => {
              await sendSESMail(
                req.user.email,
                template.subject,
                template.body,
                (attachments = [])
              );
            }
          );

          await Log.create({
            type: "subscription-updated",
            status: "active",
            data: {
              ...req.body,
              userId: req.userId,
              companyId: req.user.company.id,
              subscriptionId: newSubscription.id,
              message: "Subscription created with existing customer",
            },
          });

          return newSubscription;
        }
    } catch (error) {
        if (error.statusCode === 400 ) {
           console.error('error.error?.description', error.error?.description)
           handleError(error.error?.description, "Error - updateSubscription");
        }
        handleError(error, "Error - updateSubscription");
    }
};

const calculateProratedCharge = async ({subscriptionId, olderQuantity, newQuantity, olderPlanId, newPlanId, subscriptionStartDate, subscriptionEndDate, updatedPlanAmount}) => {
    try {
        // Step 1: Fetch subscription and plan details
        const olderPlan = RAZORPAY_PLAN_AMOUNT[olderPlanId]

        const currentPlanAmount = olderPlan.unit_amount / 100; // Lite: ₹50
        const newPlanAmount = updatedPlanAmount / 100; // Pro: ₹100

        const currentCycleStart = moment(subscriptionStartDate);
        const currentCycleEnd = moment(subscriptionEndDate);
        const totalDaysInCycle = currentCycleEnd.diff(currentCycleStart, "days");
        const daysUsed = moment().diff(currentCycleStart, "days");
        const daysLeft = totalDaysInCycle - daysUsed;
    
        const effectiveDaysLeft = daysLeft > 0 ? daysLeft : 0;

        const dailyCostOld = currentPlanAmount / totalDaysInCycle; // ₹1.67/day
        const dailyCostNew = newPlanAmount / totalDaysInCycle; // ₹3.33/day


        const creditOld = (dailyCostOld * effectiveDaysLeft)*olderQuantity; // ₹33.40 if effective days left is 20
        const creditNew = (dailyCostNew * effectiveDaysLeft)*newQuantity; // ₹66.60 if effective days left is 20

        const netUpgradeCost = creditNew - creditOld; // ₹33.20

        // If decreasing quantity, return 0 (changes will apply in next billing cycle)
        if (netUpgradeCost<0) {
            const vacantUsers = Math.abs(Math.round(netUpgradeCost / dailyCostOld)); // Number of vacant users
            console.log(`Vacant users due to downgrade: ${vacantUsers}`);

            // Do not refund but adjust vacant users in the system (e.g., update database with vacantUser count)
            const vacantUserCount = Math.max(vacantUsers, 1); // Ensure at least 1 user is marked as vacant if there's a reduction

            // Mark vacant users in the database (you can adjust the logic to store vacant users as needed)
            console.log(`Marking ${vacantUserCount} user(s) as vacant.`);
                        
            return -1;  // No refund (but the vacant user count should be updated in the system)

        }


        console.log({
            totalAmount: `₹${currentPlanAmount.toFixed(2)}`,
            daysRemaining: effectiveDaysLeft,
            totalDays: totalDaysInCycle,
            dailyCostNew: `₹${dailyCostNew.toFixed(3)}`,
            dailyCostOld: `₹${dailyCostOld.toFixed(3)}`,
            quantityChange: `${olderQuantity} → ${newQuantity}`,
            proratedAmount: `₹${Math.round(netUpgradeCost)}`,
          });
        return Math.round(netUpgradeCost);
    } catch (error) {
        console.error("Error calculating prorated charge:", error);
        throw error;
    }
};

const getRazorpayInvoiceList = async (req) => {
    try {
        return dbService.getAllDocuments(Invoice, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error - Invoice list fetch error');
        throw error;
    }
}

const capturePaymentWebhook = async (req, res) => {
    try {
        const signature = req.headers["x-razorpay-signature"];
    
        const payload = JSON.stringify(req.body);
        // Generate the expected signature using the webhook secret and the request payload
        const expectedSignature = crypto
            .createHmac("sha256", RAZORPAY.WEBHOOK_SECRET)
            .update(payload)
            .digest("hex");

        if (signature === expectedSignature) {
            const event = req.body;
            if (event.event === "subscription.activated") {
                console.log("Subscription activated:", event.payload);
            }
            res.sendStatus(200);
        } else {
            console.error("Invalid signature")
            return false
        }
        // const { paymentId, amount } = req.body;
        // const capturedPayment = await capturePayment(paymentId, amount);
        // return capturedPayment;
        return true;
    } catch (error) {
        handleError(error, "Error - capturePaymentWebhook");
    }
};

const invoicePaidWebhook = async (req,res) => {
    console.log('Invoice paid webhook started');

    const event = req.body;
    console.log("🚀 ~ invoicePaidWebhook ~ event:", JSON.stringify(event, null, 2))
    
    // Handle the invoice paid event
    if (event.event === 'invoice.paid') {
        //Fetch the company details from the user 

        const invoiceData = event.payload.invoice.entity;
        const user_company = await User.findOne({ email: invoiceData.customer_details.email }, { company: 1 });
        
        logger.info('invoice.paid started to add to database');

        // const storageRequestId = event.data.object.metadata["Storage Request Id"];
        
        const data = {
            invoiceId: invoiceData.id,
            description: invoiceData.description,
            email: invoiceData.customer_details.email,
            amount_due: invoiceData.amount_due,
            amount_paid: invoiceData.amount_paid,
            invoice_pdf: invoiceData.short_url || '',
            company: user_company?.company,
            is_subscription: invoiceData.subscription_id ? true : false,
            status: invoiceData.status || '',
            total: invoiceData.amount || 0,
            gateway: 'RAZORPAY',
            amount_currency: invoiceData.currency || 'INR',
        }

        try {
            await dbService.createDocument(Invoice, data);     
            logger.info('Invoice paid data added to database');
            return {
                success: true,
                message: 'Invoice paid data added to database'
            };
        } catch (error) {
            handleError(error, 'Error - adding invoice data to database');
            return {
                success: false,
                message: 'Error - adding invoice data to database'
            };
        }
    }
}

const subscriptionActivityWebhook = async (req, res) => {
    try {
        const webhookEvent = req.body;

        const signature = req.headers["x-razorpay-signature"];
        const payload = webhookEvent.event === "invoice.paid" ? webhookEvent : JSON.stringify(req.body);
        const expectedSignature = crypto
            .createHmac("sha256", RAZORPAY.WEBHOOK_SECRET)
            .update(req.rawBody)
            .digest("hex");

        logger.info(`signature === expectedSignature, ${webhookEvent.event}`, signature === expectedSignature);

        if (signature === expectedSignature) {
            switch(webhookEvent.event){
                case "subscription.activated":
                    updateSubscriptionInDb(req,webhookEvent.event, webhookEvent)
                    break;
                case "subscription.updated":
                    updateSubscriptionInDb(req,webhookEvent.event, webhookEvent)
                    break;
                case "subscription.cancelled":
                    updateSubscriptionInDb(req,webhookEvent.event, webhookEvent)
                    break;
                case "subscription.charged":
                    updateSubscriptionInDb(req,webhookEvent.event, webhookEvent)
                    break;
                case "invoice.paid":
                    await invoicePaidWebhook(req, res);
                    break;
                case "subscription.authenticated":
                    updateSubscriptionInDb(req,webhookEvent.event, webhookEvent)
                    break;
                default:
                    console.log(`New event received: ${webhookEvent}`)
                   logger.info(`New event received: ${webhookEvent.event}`)
                    break;
            }
            return {
                success: true,
                message: 'Webhook processed successfully'
            };
        } else {
            console.error("Signature verification failed");
            return {
                success: false,
                message: 'Invalid signature'
            };
        }
    } catch (error) {
        handleError(error, 'Error - subscriptionActivityWebhook');
    }
};

const cancelSubscription = async (req)=>{
    try { 
        const subscriptionRecord = await checkSubscription(req);

        if (!subscriptionRecord) return false;

        if (subscriptionRecord.status === RAZORPAY_SUBSCRIPTION_TYPE.CANCEL) {
            throw new Error(_localize('subscription.alreadyCancel', req, ''));
        }

        const cancelSub = await razorpay.subscriptions.cancel(subscriptionRecord.subscriptionId, {
            cancel_at_cycle_end: true
        });

        if (!cancelSub) {
          console.error("cancelSubscription ~ cancelSub: ",cancelSub);
          return false;
        }

        const formattedCancelDate = moment.unix(cancelSub.charge_at).format(MOMENT_FORMAT);

        const subscriptionUpdate = await Subscription.updateOne(
            { 'company.id': req.user.company.id },
            {
                $set: {
                    status: RAZORPAY_SUBSCRIPTION_TYPE.PENDING_CANCELLATION,
                    cancelAt: formattedCancelDate,
                    cancellation_reason: req.body.cancel_reason,
                    unCancelAt: null
                }
            }
        );

        const emailData = {
            name: req.user.fname + ' ' + req.user.lname,
            cancellation_date: formattedCancelDate
        }   

        getTemplate(EMAIL_TEMPLATE.CANCEL_SUBSCRIPTION, emailData).then(async (template) => {
            await sendSESMail(req.user.email, template.subject, template.body, attachments = [])
        })

        await Log.create({
            type: 'subscription-canceled',
            status: 'canceled',
            data: {
                ...req.body,
                userId: req.userId,
                companyId: req.user.company.id,
                subscriptionId: subscriptionRecord.subscriptionId
            }
        });

        return subscriptionUpdate;
    }catch(error){
        handleError(error,`Error - cancelRazorpaySubscription`)
    }

}

const uncancelSubscription = async (req) => {
    try {
        const subscriptionRecord = await checkSubscription(req);

        if (!subscriptionRecord) {
            throw new Error(_localize('module.notFound', req, 'Subscription'));
        }
    
        const subscriptionUpdate = await Subscription.updateOne(
            { 'company.id': req.user.company.id },
            {
              $set: {
                status: SUBSCRIPTION_TYPE.ACTIVE,
                unCancelAt: new Date()
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

        await Log.create({
            type: 'subscription-uncanceled',
            status: 'uncanceled',
            data: {
                ...req.body,
                userId: req.userId,
                companyId: req.user.company.id,
                subscriptionId: subscriptionRecord.subscriptionId
            }
        });
        
        return subscriptionUpdate;
    } catch (error) {
        console.error('Error uncancelling subscription:', error);
        throw error;
    }
}

const getPaymentMethods = async (req) => {
    try {
        // const subscriptionRecord = await checkSubscription(req);
        const response = await razorpay.customers.fetchTokens('cust_QREmXpzoTpJMvZ');
        console.log("🚀 ~ getPaymentMethods ~ response:", JSON.stringify(response, null, 2))
    
        // if (response.items.length === 0) {
        //     return { success: true, cards: [] };
        // }
    
        // // Extract unique card details
        // const uniqueCardsMap = new Map();
        // response.items.forEach(token => {
        //     if (!token.card) return; // Skip if card details are missing
    
        //     const key = `${token.card.last4}-${token.card.network}`; 
    
        //     if (!uniqueCardsMap.has(key)) {
        //         uniqueCardsMap.set(key, {
        //             // id: token.id,
        //             last4: token.card.last4,
        //             network: token.card.network,
        //             type: token.card.type || "N/A",
        //             // expiry_month: token.card.expiry_month || "N/A",
        //             // expiry_year: token.card.expiry_year || "N/A",
        //         });
        //     }
        // });
    
        // const uniqueCards = Array.from(uniqueCardsMap.values());
        return uniqueCards;
    
    } catch (error) {
        console.error('Error - getPaymentMethods:', error);
        handleError(error, 'Error - getPaymentMethods');
    }
}

const unCancelCreateSubscription = async (subscriptionData) => {
    try {

        // Create the subscription with immediate charging
        const newUnCancelSubscription = await razorpay.subscriptions.create(subscriptionData);

        // Rest of your code remains the same
        await Subscription.updateOne(
            { "customerId": subscriptionData.customer_id },
            {
                $set: {
                    subscriptionId: newUnCancelSubscription.id,
                    startDate: moment.unix(newUnCancelSubscription.start_at).format(MOMENT_FORMAT),
                    endDate: moment.unix(newUnCancelSubscription.end_at).format(MOMENT_FORMAT),
                    status: SUBSCRIPTION_TYPE.ACTIVE,
                    allowuser: newUnCancelSubscription.quantity,
                    notes: newUnCancelSubscription.notes,
                    plan: newUnCancelSubscription.plan_id,
                    planName: newUnCancelSubscription.plan_name
                },
                $unset:{
                    cancelAt: "",
                    cancellation_reason: "",
                    unCancelAt: null
                }
            }
        );

        return newUnCancelSubscription;

    
    } catch (error) {
        handleError(error, 'Error - unCancelCreateSubscription');
    }
}

const deductAmountOnce = async (customerId, tokenId, amount, method) => {
  try {
    // Create an order first
    const order = await razorpay.orders.create({
      amount: amount, // Amount in paise
      currency: "INR",
      receipt: `receipt_${Date.now()}`,
      notes: {
        customerId: customerId,
        tokenId: tokenId,
        description: "One-time deduction for storage"
      }
    });

    // Log the transaction
    if (order) {
      await Log.create({
        type: "one-time-payment-order",
        status: "created",
        data: {
          orderId: order.id,
          customerId: customerId,
          tokenId: tokenId,
          amount: amount,
          description: "One-time deduction for storage",
        },
      });
    }

    return order;
  } catch (error) {
    console.error("Order Creation Failed:", error);
    throw error;
  }
};

const getStoragePrice = async (req) => {
    try {
        // get plan id using storage price from razorpay using plan id
        const plan = await razorpay.plans.fetch(RAZORPAY.STORAGE_PLAN_ID);        
        return plan;
    } catch (error) {
        handleError(error, 'Error - getStoragePrice');
    }
}

const storageRequestCharge = async (req) => {
    try {
        const storageRequest = await checkStorageRequest(req.body.storageRequestId, STORAGE_REQUEST_STATUS.PENDING, req.user.company.id);
        if (!storageRequest) {
            throw new Error(_localize('module.invalid', req, 'Storage Request'));
        }

        const subscriptionRecord = await checkSubscription(req);
        if (!subscriptionRecord) {
            throw new Error(_localize('subscription.noSubscription', req, ''));
        }

        const response = await razorpay.customers.fetchTokens(subscriptionRecord.customerId);
    
        if (response.items.length === 0) {
            throw new Error(_localize('module.invalid', req, 'Payment Method'));
        }

        // Get amount in paise (multiply by 100 if your amount is in rupees)
        const amountInPaise = req.body.amount;
        
        // Create order for frontend checkout
        const order = await deductAmountOnce(
            subscriptionRecord.customerId, 
            response.items[0].token, 
            amountInPaise, 
            response.items[0].method
        );
        
        // Return order details to frontend
        return {
            success: true,
            order: order,
            storageRequestId: storageRequest.id,
            amount: amountInPaise,
            currency: "INR",
            name: "Storage Upgrade",
            description: `Additional storage request of ${storageRequest?.requestSize} units`,
            prefill: {
                name: req.user.fname + " " + req.user.lname,
                email: req.user.email,
                contact: req.user.contact || ""
            }
        };
    } catch (error) {
        handleError(error, 'Error - storageRequestCharge');
        throw error;
    }
};

const verifyStoragePayment = async (req) => {
    try {
        const {
            razorpay_payment_id,
            razorpay_order_id,
            razorpay_signature,
            storageRequestId
        } = req.body;
        // Verify signature
        const hmac = crypto.createHmac('sha256', RAZORPAY.KEY_SECRET);
        hmac.update(`${razorpay_order_id}|${razorpay_payment_id}`);
        const generatedSignature = hmac.digest('hex');

        if (generatedSignature !== razorpay_signature) {
            throw new Error(_localize('payment.invalidSignature', req, ''));
        }

        // Get storage request
        const storageRequest = await checkStorageRequest(storageRequestId, STORAGE_REQUEST_STATUS.PENDING, req.user.company.id);
        
        if (!storageRequest) {
            throw new Error(_localize('module.invalid', req, 'Storage Request'));
        }

       await approveStorageRequest(storageRequestId, storageRequest.requestSize);

        // Log the successful payment
        await Log.create({
            type: "storage-payment",
            status: "success",
            data: {
                paymentId: razorpay_payment_id,
                orderId: razorpay_order_id,
                storageRequestId: storageRequestId,
                amount: storageRequest.requestSize,
                userId: req.user._id,
                companyId: req.user.company.id
            }
        });

        return {
            success: true,
            message: 'Payment successful and storage request approved'
        };
    } catch (error) {
        handleError(error, 'Error - verifyStoragePayment');
        throw error;
    }
};

async function createInvoice(customerId, amount, description) {
    const invoice = await razorpay.invoices.create({
      type: 'invoice',
      customer_id: customerId,
      line_items: [
        {
          name: description || 'Payment for Subscription / Order',
          amount: amount , // Amount in paise
          currency: "INR",
          quantity: 1
        }
      ],
      description: "Invoice for received payment",
      partial_payment: false,
      email_notify:1,
      sms_notify:1
    });
    return invoice;
}

async function markInvoicePaid(invoiceId, paymentId) {
    await razorpay.invoices.markAsPaid(invoiceId, {
      payment_id: paymentId
    });
}

const createRazorpayCustomer = async (req) => {
    try {
        // const customer = await razorpay.customers.create({
        //     name: "Sample Customer",
        //     contact: "9000090000",
        //     email: "sample@example.com",
        //     fail_existing : '0',
        //     // notes: {
        //     //     company_id: req.user.company.id,
        //     //     user_id: req.user._id
        //     // }
        // });
 
        //const customerId = customer?.id;
        const customerId = 'cust_QREmXpzoTpJMvZ';

        const notes = {
            "Note 1":"Manually create order",
        }
        const token = {
            "max_amount": 100000000,
            "expire_at": 4102444799,
            "frequency": "monthly"
        }

        const order = await createRazorpayOrder(5000,"INR",notes,token,customerId);
        // const invoice = await createInvoice(customerId, 5000, "Monthly Subscription")
      
        return {
            customer: { customerId: customerId},
            order
        };
    } catch (error) {
        console.log("🚀 ~ createRazorpayCustomer ~ error:", JSON.stringify(error, null, 2))
        if (error.statusCode === 400 ) {
            console.error('error.error?.description', error.error?.description)
            handleError(error.error?.description, "Error - updateSubscription");
         }
        handleError(error, 'Error - createRazorpayCustomer');
    }
}

const fetchRazorpayToken = async (req) => {
    try {
        const response = await razorpay.payments.fetch(req.body.paymentId);
        
        return response;
    } catch (error) {
        handleError(error, 'Error - fetchRazorpayToken');
    }
}

const createRazorpayRecurringPayment = async (req) => {
    
    try {
        const {tokenId, customerId} = req.body;
        
        const notes = {
            "Note 1":"Manually create order",
        }

        const token = {
            "max_amount": 100000000,
            "expire_at": 4102444799,
            "frequency": "monthly"
        }
        const orderRes= await createRazorpayOrder(6000,"INR",notes,token,customerId);

        const recurringPayment = await razorpay.payments.createRecurringPayment({
            "email": "sample2@example.com",
            "contact": "9000090000",
            "amount": 4000,
            "currency": "INR",
            "order_id": orderRes?.id,
            "customer_id": customerId,
            "token": tokenId,
            "recurring": "1",
            "description": "Creating recurring sample payment for weam",
            "notes": {
              "note_key 1": "Using token Test payment",
              "note_key 2": "Test recurring payment"
            }
        })
        
        return recurringPayment;
    } catch (error) {
        handleError(error, 'Error - createRazorpayRecurringPayment');
    }
}

const updateSubscriptionDemo= async (req)=>{
    try {
        const {olderQuantity, newQuantity, oldPlanName, newPlanName, subscriptionStartDate, subscriptionEndDate,updateChangeDate,tokenId} = req.body;
        const proratedAmount = await calculateProratedChargeDemo({olderQuantity, newQuantity, oldPlanName, newPlanName, subscriptionStartDate, subscriptionEndDate,updateChangeDate});
       
        // proratedamount is >0 then create a new order and capture the payment
        if(proratedAmount>0){
            const order = await createRazorpayOrder(proratedAmount,"INR");

            const recurringPaymentOptions = {
                "email": "sample@example.com",
                "contact": "9000090000",
                "amount": proratedAmount,
                "currency": "INR",
                "order_id": order?.id,
                "customer_id": 'cust_QREmXpzoTpJMvZ',
                "token": tokenId,
                "recurring": "1",
                "description": "Creating recurring sample payment for weam",
                "notes": {
                  "Note 1": "Manual update payment",
                }
            }
            const recurringPayment = await razorpay.payments.createRecurringPayment(recurringPaymentOptions)
        }
    } catch (error) {
        if (error.statusCode === 400 ) {
            console.error('error.error?.description', error.error?.description)
            handleError(error.error?.description, "Error - updateSubscription");
         }
        handleError(error, 'Error - updateSubscriptionDemo');
        throw error;
    }
}

const calculateProratedChargeDemo = async ({
    olderQuantity,
    newQuantity,
    oldPlanName,
    newPlanName,
    subscriptionStartDate,
    subscriptionEndDate,
    updateChangeDate,
}) => {
    try {
        if (oldPlanName === newPlanName && olderQuantity === newQuantity) {
            return 0; // No change
        }

        // Step 1: Fetch subscription and plan details
        const olderPlan = RAZORPAY_PLAN_AMOUNT[oldPlanName];
        const newPlan = RAZORPAY_PLAN_AMOUNT[newPlanName];

        const currentPlanAmount = olderPlan.unit_amount / 100; // Lite: ₹50
        const newPlanAmount = newPlan.unit_amount / 100; // Pro: ₹100

        const currentCycleStart = moment(subscriptionStartDate);
        const currentCycleEnd = moment(subscriptionEndDate);

        const totalDaysInCycle = currentCycleEnd.diff(
            currentCycleStart,
            'days'
        );
        const effectiveChangeDate = updateChangeDate
            ? moment(updateChangeDate)
            : moment();
        const daysUsed = Math.max(
            0,
            effectiveChangeDate.diff(currentCycleStart, 'days') - 1
        );

        const daysLeft = totalDaysInCycle - daysUsed;

        const effectiveDaysLeft = daysLeft > 0 ? daysLeft : 0;
        const dailyCostOld = currentPlanAmount / totalDaysInCycle; // ₹1.67/day
        const dailyCostNew = newPlanAmount / totalDaysInCycle; // ₹3.33/day

        const creditOld = dailyCostOld * effectiveDaysLeft * olderQuantity; // ₹33.40 if effective days left is 20
        const creditNew = dailyCostNew * effectiveDaysLeft * newQuantity; // ₹66.60 if effective days left is 20
        const netUpgradeCost = (creditNew - creditOld).toFixed(2) * 100; // ₹33.20

        if (netUpgradeCost < 0) {
            if (oldPlanName === newPlanName && olderQuantity > newQuantity) {
                const vacantSeats = olderQuantity - newQuantity;
                logger.info(`Quantity downgrade: ${vacantSeats} seat(s) are now vacant.`);
            } else {
                logger.info(`Plan downgrade: ${oldPlanName} → ${newPlanName} quantityChange: ${olderQuantity} → ${newQuantity}`);
            }
            return -1; 
        }

        console.log({
            totalAmount: `₹${currentPlanAmount.toFixed(2)}`,
            daysRemaining: effectiveDaysLeft,
            totalDays: totalDaysInCycle,
            dailyCostNew: `₹${dailyCostNew.toFixed(3)}`,
            dailyCostOld: `₹${dailyCostOld.toFixed(3)}`,
            quantityChange: `${olderQuantity} → ${newQuantity}`,
            proratedAmount: `₹${netUpgradeCost}`,
        });
        return netUpgradeCost;
    } catch (error) {
        console.error('Error calculating prorated charge:', error);
        throw error;
    }
};



module.exports = {
    createSubscription,
    fetchSubscriptionPlan,
    createRazorpayOrder,
    verifySubscriptionPayment,
    getRazorpaySubscription,
    updateSubscription,
    capturePaymentWebhook,
    getRazorpayInvoiceList,
    invoicePaidWebhook,
    cancelSubscription,
    uncancelSubscription,
    subscriptionActivityWebhook,
    getPaymentMethods,
    unCancelCreateSubscription,
    updatePaymentMethod,
    storageRequestCharge,
    getStoragePrice,
    verifyStoragePayment,
    createRazorpayCustomer,
    fetchRazorpayToken,
    createRazorpayRecurringPayment,
    updateSubscriptionDemo
};