'use client';

import { useState, useEffect } from 'react';
import commonApi from '@/api';
import { MODULES, MODULE_ACTIONS, DEFAULT_SORT } from '@/utils/constant';
import { getCompanyId, getCurrentUser } from '@/utils/handleAuth';
import Toast from '@/utils/toast';

export type UserCreditData = {
  _id: string,
  fname: string;
  lname: string;
  email: string;
  roleCode: string;
  msgCredit: number;
  usedCredits?: number;
  leftCredits?: number;
}

export type CreditAllocationStats = {
  availableCredits: number;
  totalAllocated: number;
}

const useCreditAllocation = () => {
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<UserCreditData[]>([]);
  const [stats, setStats] = useState<CreditAllocationStats>({
    availableCredits: 0,
    totalAllocated: 0
  });
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const getUsersForCreditAllocation = async (
    search = '',
    limit = 10,
    offset = 0
  ) => {
    try {
      setLoading(true);
      const currentUser = getCurrentUser();
      const companyId = getCompanyId(currentUser);
      
      const searchColumns = ['email', 'roleCode', 'fname', 'lname'];
      
      const query = {
        $or: [
          ...searchColumns.map(column => ({
            [column]: { $regex: search, $options: 'i' }
          })),
          { $expr: { $regexMatch: { input: { $concat: ['$fname', ' ', '$lname'] }, regex: search, options: 'i' } } }
        ],
        'company.id': companyId,
        inviteSts: 'ACCEPT' 
      };

      const response = await commonApi({
        action: MODULE_ACTIONS.LIST,
        prefix: MODULE_ACTIONS.ADMIN_PREFIX,
        module: MODULES.USER,
        common: true,
        data: {
          options: {
            offset,
            limit,
            sort: {
              createdAt: -1,
            },
          },
          query,
          needUsedCredits: true
        },
      });
      // Transform the data to include credit information
      const transformedUsers = response.data.map((user: any) => ({

        _id: user._id,
        fname: user.fname || '',
        lname: user.lname || '',
        name: `${user.fname || ''} ${user.lname || ''}`.trim() || user.email,
        email: user.email,
        role: user.roleCode || 'USER',
        totalCredits: user.msgCredit || 0,
        leftCredits: (user.msgCredit - (user.usedCredits || 0)).toFixed(2) || 0,
        usedCredits: user.usedCredits || 0,
      }));

      setUsers(transformedUsers);
      setTotalRecords(response?.paginator?.itemCount || 0);
      setTotalPages(response?.paginator?.pageCount || 0);

      // Calculate stats
      const totalAllocated = transformedUsers.reduce((sum, user) => sum + user.allocatedCredits, 0);
      setStats({
        availableCredits: 500, // This should come from company/organization data
        totalAllocated
      });

    } catch (error) {
      console.error('Error fetching users for credit allocation:', error);
      Toast('Failed to fetch users', 'error');
    } finally {
      setLoading(false);
    }
  };

  const updateUserCredits = async (userIds: string[], credits: number) => {
    try {
      setLoading(true);

      const userEmails = userIds.map((currSelectUser) => {
        const user = users.find(user => user._id === currSelectUser)?.email;
        return user;
      });
      
      const response = await commonApi({
        action: MODULE_ACTIONS.ADD_CREDIT,
        data: {
          ids: userIds,
          credit: credits,
          email: userEmails
        },
      });

      Toast(response.message || 'User credits updated successfully', 'success');
      
      // Refresh the user list
      await getUsersForCreditAllocation();
      
      return response;
    } catch (error) {
      console.error('Error updating user credits:', error);
      Toast('Failed to update user credits', 'error');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    users,
    stats,
    loading,
    totalRecords,
    totalPages,
    getUsersForCreditAllocation,
    updateUserCredits
  };
};

export default useCreditAllocation; 