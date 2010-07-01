#ifndef B2BUA_CC_EVENT_HPP_
#define B2BUA_CC_EVENT_HPP_


/**************** Copyright (C) 2005 by SIEMENS AG *****************************
  This program contains proprietary information which is a
  trade secret of SIEMENS AG, Munich, and also is protected
  as an unpublished work under applicable Copyright laws.
  The program is to be retained in confidence.
  Any use by third parties (e.g. use as a control program,
  reproduction, modification and translation) is governed
  solely by written agreements with SIEMENS AG.
*******************************************************************************/

/** @file B2buaCcEvent.hpp.
 * 
 *  Call control event and mapping support of SIP-User-Id to CC-User-Ids
 *
 *  @author groetinc
 *  --------------------------------------------------------------------------------
 *  | User-Id       |----------------------------------------------------|
 *  | *1 (FXS1)     | 0 - CC_USER_FXS1             CC_USER_SIP_MSN1 - 5  | --> MSN1
 *  | *2 (FXS2)     |     CC_USER_FXS2             CC_USER_SIP_MSN2 - 6  | --> MSN2
 *  | *3 (VOIP1)    |     CC_USER_VOIP_CLIENT1     CC_USER_SIP_MSN3 - 7  | --> MSN3
 *  | *4 (VOIP2)    |     CC_USER_VOIP_CLIENT1     CC_USER_SIP_MSN4 - 8  | --> MSN4
 *  | *5 (VOIP3)    |     CC_USER_VOIP_CLIENT1     CC_USER_SIP_MSN5 - 9  | --> MSN5
 *  | *6 (VOIP4)    |     CC_USER_VOIP_CLIENT1     CC_USER_SIP_MSN6 - 10 | --> MSN6
 *  | RGW           |     CC_USER_RGW              CC_USER_FXO_GW   - 11 | --> FXO
 *  |               |----------------------------------------------------|
 *  --------------------------------------------------------------------------------
 */
/***********************************************************************************/

//==============================================================================
// Includes
//==============================================================================
/* Library Includes */

/* System Includes */
#include "event.h"
#include "ua_types.h"
#include "b2bua_types.hpp"

/* Component Includes */

namespace b2bua {
  
  
/******************************************************************************/
/** @class B2buaCcEvent.
 * 
 * B2BUA CC event class definition.
 */ 
/******************************************************************************/
class B2buaCcEvent
{
public:
                                  // Constructor for incomming events
  B2buaCcEvent(Ebf::Event *pEvent);
                                  // Constructor for outgoing events
  B2buaCcEvent(Ebf::Event *pEvent, CcUserReferenceType ccUserRef);
  ~B2buaCcEvent();
  
  CcUserReferenceType   getCcUserRef(void);
  call_ref_type getCallRef(void);
  static void ConfigureInternalUserIds(Ebf::Event *pEvent);
  void  dispatch();
  
  Ebf::Event            *_pEvent;

  CcUserReferenceType mapUserName2UserRef(char* pcUID);
    
private:

  void processIncUserRef();
  void processOutUserRef();

  CcUserReferenceType   _ccUserRef;
  call_ref_type         _callRef;
  
};

extern const user_ref_type cc_user_ref_to_sip_user_ref_map[];
extern const CcUserReferenceType sip_user_ref_to_cc_user_ref_map[];

} // namespace b2bua


#endif /*B2BUA_CC_EVENT_HPP_*/
