



~~~cpp
//@AndroidImsRadioModule.cpp
//path qcril-hal/modules/android_ims_radio/src/AndroidImsRadioModule.cpp
void AndroidImsRadioModule::handleQcRilUnsolIncomingImsSMSMessage(
    std::shared_ptr<RilUnsolIncomingImsSMSMessage> msg) {
  Log::getInstance().d("[" + mName + "]: Handling msg = " + msg->dump());
  if (mImsRadio != nullptr) {
    mImsRadio->notifyIncomingImsSms(msg);
  }
}
~~~





~~~cpp
//@qcril_qmi_ims_radio_service.cpp
//path qcril-hal/modules/android_ims_radio/src/hidl_impl/base/qcril_qmi_ims_radio_service.cpp

void ImsRadioImpl::notifyIncomingImsSms(std::shared_ptr<RilUnsolIncomingImsSMSMessage> msg) {
    if (msg) {
        sp<V1_2::IImsRadioIndication> indCb1_2 = getIndicationCallbackV1_2();
        if (indCb1_2) {
            V1_2::IncomingImsSms sms;
            auto tech = msg->getTech();
            if (tech == RADIO_TECH_3GPP) {
                auto& payload = msg->getGsmPayload();
                sms = {"3gpp", payload, convertVerificationStatus(
                        msg->getVerificationStatus())};
            } else {
                std::vector<uint8_t> payload;
                (void)convertCdmaFormatToPseudoPdu(msg->getCdmaPayload(), payload);
                sms = {"3gpp2", payload, V1_2::VerificationStatus::STATUS_VALIDATION_NONE};
            }
            imsRadiolog("<", "onIncomingImsSms: sms = " + toString(sms));
            Return<void> ret = indCb1_2->onIncomingImsSms(sms);
            if (!ret.isOk()) {
                QCRIL_LOG_ERROR("Unable to send response. Exception : %s",
                        ret.description().c_str());
            }
        } else {
            QCRIL_LOG_ERROR("V1_2 indication cb is null");
        }
    }
}
~~~







~~~java
//@ImsSenderRxrjava
//commonsys/telephony-apps/ims/src/org/codeaurora/ims/ImsSenderRxr.java
public void onIncomingImsSms(IncomingImsSms imsSms) {
    unsljLog(MessageId.UNSOL_INCOMING_IMS_SMS);
    if(imsSms.pdu!=null && imsSms.format!=null){
        IncomingSms newSms = ImsRadioUtils.incomingSmsfromHidl(imsSms);
        if(mIncomingSmsRegistrant!=null) {
            mIncomingSmsRegistrant.notifyRegistrant(new AsyncResult(null, newSms, null));
        }
    }
}
~~~



