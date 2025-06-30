const User = require('../models/user');
const Thread = require('../models/thread');
const Company = require('../models/company');
const mongoose = require('mongoose');
const { INVITATION_TYPE } = require('../config/constants/common');
const { dateForMongoQuery, getDateRangeByCode, createPaginator } = require('../utils/helper');


const getCompanyUsage = async (req) => {
    try {
        //Condition for message tbl
        const matchConditions = {
            'threadDetails.openai_error': { $exists: false },
            "threadDetails.importId": { $exists: false }, 
        };

        if(req?.body?.isPaid !== ''){
            matchConditions['threadDetails.isPaid'] = req?.body?.isPaid;
        }
        
        if (req.body.modelCode.length > 0) {
            matchConditions['threadDetails.responseModel'] = { $in: req.body.modelCode };
        }

        if (req.body.startDate && req.body.endDate) {
            matchConditions['threadDetails.createdAt'] = {
                $gte: new Date(dateForMongoQuery(req.body.startDate, true)),
                $lte: new Date(dateForMongoQuery(req.body.endDate, false))
            };
        }

        //Condition for user tbl
        const userMatchConditions = {
            'company.id': req.user.company.id,
            inviteSts: INVITATION_TYPE.ACCEPT,
        }
        
        if (req.body.query.search != '') {
            const search = req.body.query.search;
            userMatchConditions['$or'] = [
                { fname: { $regex: search, $options: 'i' } },    
                { lname: { $regex: search, $options: 'i' } },    
                { email: { $regex: search, $options: 'i' } }  
            ];
        }
        
        // Query to get the total number of records
        const totalRecordsPipeline = [
            {
                $match: userMatchConditions
            },
            {
                $lookup: {
                    from: 'messages',
                    localField: '_id',
                    foreignField: 'user.id',
                    as: 'threadDetails'
                }
            },
            {
                $unwind: {
                    path: '$threadDetails',
                    preserveNullAndEmptyArrays: true
                }
            },
            {
                $match: matchConditions
            },
            {
                $group: {
                    _id: '$_id',
                    msgCount: { $sum: { $cond: [{ $gt: ['$threadDetails', null] }, 1, 0] } }
                }
            },
            {
                $count: 'totalRecords'
            }
        ];

        const totalRecordsResult = await User.aggregate(totalRecordsPipeline);

        const itemCount = totalRecordsResult[0]?.totalRecords || 0;
        const perPage = req.body.options.limit;
        const offset = req.body.options.offset;
        const currentPage = Math.floor(offset / perPage) + 1;
        const pageCount = Math.ceil(itemCount / perPage);
        const sorting = req.body.options.sort;

        const aggregationPipeline = [
            {
                $match: userMatchConditions
            },
            {
                $lookup: {
                    from: 'messages',
                    localField: '_id',
                    foreignField: 'user.id',
                    as: 'threadDetails'
                }
            },
            {
                $unwind: {
                    path: '$threadDetails',
                    preserveNullAndEmptyArrays: true
                }
            },
            {
                $match: matchConditions
            },
            {
                $group: {
                    _id: '$_id',
                    userId: { $first: '$_id' },
                    msgCount: { $sum: { $cond: [{ $gt: ['$threadDetails', null] }, 1, 0] } },
                    totalUsedCredit: { $sum: "$threadDetails.usedCredit" }, 
                    fname: { $first: '$fname' },
                    lname: { $first: '$lname' },
                    email: { $first: '$email' },
                    usedSize: { $first: '$usedSize' }
                }
            },
            {
                $sort : sorting
            },
            { $skip: offset },
            { $limit: perPage }
        ];
        
        const result = await User.aggregate(aggregationPipeline);

        const pagination = createPaginator(itemCount, offset, perPage);

        return {
            data: result, 
            paginator: pagination
        };
    } catch (error) {
        handleError(error, 'Error - getCompanyUsage')
    }
}

const getUserUsage = async (req) => {
    try {
        const matchConditions = {
            companyId: new mongoose.Types.ObjectId(req.user.company.id),
            openai_error: { $exists: false },
            'user.id': new mongoose.Types.ObjectId(req.userId),
            importId: { $exists: false }
        };
        
        if(req?.body?.isPaid !==  ''){
            matchConditions['isPaid'] = req?.body?.isPaid;
        }
        
        if (req.body.modelCode.length > 0) {
            matchConditions['responseModel'] = { $in: req.body.modelCode };
        }

        if (req.body.startDate && req.body.endDate) {
            matchConditions['createdAt'] = {
                $gte: new Date(dateForMongoQuery(req.body.startDate, true)),
                $lte: new Date(dateForMongoQuery(req.body.endDate, false))
            };
        }
        
        // Count total records
        const totalRecordsPipeline = [
            { $match: matchConditions },
            { $group: { _id: '$responseModel' } },
            { $count: 'totalRecords' }
        ];

        const totalRecordsResult = await Thread.aggregate(totalRecordsPipeline);
        const itemCount = totalRecordsResult[0]?.totalRecords || 0;

        const perPage = req.body.options.limit;
        const offset = req.body.options.offset;
        const currentPage = Math.floor(offset / perPage) + 1;
        const pageCount = Math.ceil(itemCount / perPage);
        const sorting = req.body.options.sort;

        const aggregationPipeline = [
            { $match: matchConditions },
            {
                $group: {
                    _id: '$responseModel',
                    msgCount: { $sum: 1 },
                    totalUsedCredit: { $sum: "$usedCredit" }, 
                    model: { $first: '$responseModel' },
                    modeldata: { $first: '$model' },
                    'credit': { $sum: '$credit' }
                },
            },
            {
                $sort : sorting
            },
            { $skip: offset },
            { $limit: perPage }
        ];

        const msgCounts = await Thread.aggregate(aggregationPipeline);

        const pagination = createPaginator(itemCount, offset, perPage);

        // Wrap the data and pagination in the desired structure
        return {
            data: msgCounts, 
            paginator: pagination
        };
    } catch (error) {
        handleError(error, 'Error - getUserUsage')
    }
}

const getWeeklyUsage = async (req) => {
    try {
        let dateRanges = [];
        let matchConditions = {};
        let isDirectDateRange = false;

        // Check if direct start and end dates are provided
        if (req.body.startDate && req.body.endDate && !req.body.exportCode) {
            isDirectDateRange = true;
            
            dateRanges = [{
                label: 'Total Messages',
                start: new Date(dateForMongoQuery(req.body.startDate, true)),
                end: new Date(dateForMongoQuery(req.body.endDate, false))
            }];
        } else {
            dateRanges = await getWeeklyDateRanges(req?.body?.exportCode);            
        }
        
        if (req.body.query.search != '') {
            const search = req.body.query.search;
            matchConditions['$or'] = [
                { companyNm: { $regex: search, $options: 'i' } },
                { 'UserDetails.fname': { $regex: search, $options: 'i' } },
                { 'UserDetails.lname': { $regex: search, $options: 'i' } },
                { 'UserDetails.email': { $regex: search, $options: 'i' } }
            ];
        }

        // Add subscription filter conditions
        if (req.body.planCode === 'paid' && !req.body.exportCode) {
            matchConditions['SubscriptionDetails'] = { $ne: [] };
        } else if (req.body.planCode === 'free' && !req.body.exportCode) {
            matchConditions['SubscriptionDetails'] = { $eq: [] };
        }
        
        //Set
        const dynamicFields = {};
        let columnHeaders = [];
        dateRanges.forEach(range => {
            //Set dynamic fields for  query
            dynamicFields[range.label] = {
              $size: {
                $filter: {
                  input: "$MessageDetails",
                  as: "msg",
                  cond: {
                    $and: [
                      { $gte: ["$$msg.createdAt", range.start] },
                      { $lte: ["$$msg.createdAt", range.end] }
                    ]
                  }
                }
              }
            };

            //Set column data for frontend datatable
            columnHeaders.push({
                accessorKey: range.label,
                header: range.label,
                enableSorting: false
            });
        });

        const projectStage = {
            _id: 1,
            companyNm: 1,
            createdAt: 1,
            countryName: 1,
            countryCode: 1,
            email: 1,
            totalMember: 1,
            username: 1,
            hasSubscription: 1
        };
          
        // Add dynamic message count fields
        dateRanges.forEach(range => {
            projectStage[range.label] = 1;
        });

        // Calculate pagination parameters
        const perPage = req.body.options.limit;
        const offset = req.body.options.offset;
        const currentPage = Math.floor(offset / perPage) + 1;

        const commonLookupAndAddFields = [
            {
                $lookup: {
                    from: "messages",
                    let: { companyId: "$_id" },
                    pipeline: [
                        {
                            $match: {
                                $expr: { $eq: ["$companyId", "$$companyId"] },
                                // Add date filter for messages if using direct date range
                                ...(isDirectDateRange && {
                                    createdAt: {
                                        $gte: dateRanges[0].start,
                                        $lte: dateRanges[0].end
                                    }
                                }),
                                ...(req.body.planCode ? { isPaid: req.body.planCode === 'paid' ? true : false } : {}),
                                'openai_error': { $exists: false },
                                'importId': { $exists: false },                                
                            }
                        },
                        {
                            $project: { _id: 1, companyId: 1, createdAt: 1 }
                        }
                    ],
                    as: "MessageDetails"
                }
            },
            {
                $lookup: {
                    from: "user",
                    localField: "_id",
                    foreignField: "company.id",
                    as: "UserDetails",
                },
            },
            {
                $lookup: {
                    from: "subscription", // Replace with your actual subscription collection name
                    localField: "_id",
                    foreignField: "company.id", // Replace with the actual field name that references company
                    as: "SubscriptionDetails"
                }
            },
            {
                $addFields: {
                    "username": {
                        $arrayElemAt: [
                            {
                                $map: {
                                    input: {
                                        $filter: {
                                            input: "$UserDetails",
                                            as: "user",
                                            cond: { $eq: ["$$user.roleCode", "COMPANY"] },
                                        },
                                    },
                                    as: "filteredUser",
                                    in: { $concat: ["$$filteredUser.fname", " ", "$$filteredUser.lname"] }
                                },
                            },
                            0,
                        ],
                    },
                    "email": {
                        $arrayElemAt: [
                            {
                                $map: {
                                    input: {
                                        $filter: {
                                            input: "$UserDetails",
                                            as: "user",
                                            cond: { $eq: ["$$user.roleCode", "COMPANY"] },
                                        },
                                    },
                                    as: "filteredUser",
                                    in: "$$filteredUser.email",
                                },
                            },
                            0,
                        ],
                    },
                    "totalMember": { $size: "$UserDetails" },
                    "hasSubscription": { $gt: [{ $size: "$SubscriptionDetails" }, 0] },
                    ...dynamicFields
                }
            }
        ];

        const aggregationPipeline = [
            { $sort: { "createdAt": -1 } }
        ];
        
        if (!req?.body?.exportCode) {
            aggregationPipeline.push(
                { $skip: offset },
                { $limit: perPage }
            );
        }

        // Use the common query part in totalRecordsPipeline
        const totalRecordsPipeline = [
            ...commonLookupAndAddFields,
            { $match: matchConditions },
            { $count: 'totalRecords' }
        ];
        
        //Get total records
        const totalRecordsResult = await Company.aggregate(totalRecordsPipeline);
        const itemCount = totalRecordsResult[0]?.totalRecords || 0;
        const pageCount = Math.ceil(itemCount / perPage);
        
        // Use the common query part in the main aggregation pipeline
        const result = await Company.aggregate([
            ...commonLookupAndAddFields,
            { $match: matchConditions },
            { $project: projectStage },
            ...aggregationPipeline
        ]);

        return !req?.body?.exportCode ? {
            data: {
                msgCountResult: result,
                weeklyDateRanges: columnHeaders
            },
            paginator: createPaginator(itemCount, offset, perPage)
        } : {
            data: {
                msgCountResult: result,                
            }            
        };
    } catch (error) {
        handleError(error, 'Error - getWeeklyUsage');
    }
}

const getWeeklyDateRanges = async (requestCode) => {
    const { startDate, endDate } = await getDateRangeByCode(requestCode);
    
    // Align startDate to previous Monday
    const dayOfWeek = startDate.getUTCDay();
    const daysToMonday = (dayOfWeek + 6) % 7;
    startDate.setUTCDate(startDate.getUTCDate() - daysToMonday);
  
    const weeks = [];
    let current = new Date(startDate);
    
    while (current <= endDate) {
        const weekStart = new Date(Date.UTC(
            current.getUTCFullYear(),
            current.getUTCMonth(),
            current.getUTCDate(),
            0, 0, 0
        ));
        
        const weekEnd = new Date(Date.UTC(
            current.getUTCFullYear(),
            current.getUTCMonth(),
            current.getUTCDate() + 6,
            23, 59, 59
        ));
        const label = `${weekStart.toLocaleString('en-US', { month: 'short' })}${weekStart.getUTCDate()}-${weekEnd.toLocaleString('en-US', { month: 'short' })}${weekEnd.getUTCDate()}`;

        weeks.push({
            label: label,
            start: weekStart,
            end: weekEnd
        });
        
        current.setUTCDate(current.getUTCDate() + 7);
    }
    
    return weeks;
}

module.exports = {
    getCompanyUsage,
    getUserUsage,
    getWeeklyUsage
}