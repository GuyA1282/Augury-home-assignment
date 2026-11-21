*** Settings ***
Library       ../augury_api.py
Test Setup    Api Reset

*** Variables ***
${RETRIES}     3x
${INTERVAL}    1s

*** Test Cases ***
OTA Happy Flow
    Given A Node At Version    MOXA    MOXA_X    ${33}
    When Artifact Is Posted To The Node Channel    MOXA_X    moxa_34.swu
    Then The Node Version Should Become    MOXA_X    ${34}
    And The Node Should Have No Error    MOXA_X

Bad Firmware OTA Is Rejected
    Given A Node At Version    CASSIA    CASSIA_X    ${33}
    When Artifact Is Posted To The Node Channel    CASSIA_X    moxa_34.swu
    Then The Node Should Report An Error    CASSIA_X
    And The Node Version Should Be    CASSIA_X    ${33}

DFU Waits For Backlog To Drain
    Given A Node At Version    MOXA    MOXA_X    ${33}
    And An Endpoint    EP1    EP1_001    ${3000}    ${33}    ${5}    MOXA_X
    When DFU Is Triggered    EP1_001    ${34}
    Then The Endpoint Version Should Be    EP1_001    ${33}
    When The Backlog Is Drained    EP1_001
    And DFU Is Triggered    EP1_001    ${34}
    Then The Endpoint Version Should Be    EP1_001    ${34}

DFU Is Deferred On Low Battery
    Given A Node At Version    MOXA    MOXA_X    ${33}
    And An Endpoint    Canary_A    CAN_001    ${3500}    ${33}    ${0}    MOXA_X
    When DFU Is Triggered    CAN_001    ${34}
    Then The Endpoint Version Should Be    CAN_001    ${33}

Post To Unknown Channel Is Rejected
    ${status}=    Api Post Version To Ota Channel    OTA_UNKNOWN    moxa_34.swu
    Should Be Equal As Integers    ${status}    400

*** Keywords ***
A Node At Version
    [Arguments]    ${type}    ${uuid}    ${version}
    Api Create Node    ${type}    ${uuid}    ${version}

An Endpoint
    [Arguments]    ${type}    ${serial}    ${battery}    ${version}    ${backlog}    ${node_uuid}
    Api Create Endpoint    ${type}    ${serial}    ${battery}    ${version}    ${backlog}    ${node_uuid}

Artifact Is Posted To The Node Channel
    [Arguments]    ${uuid}    ${artifact}
    ${node}=    Api Get Node By Uuid    ${uuid}
    ${status}=    Api Post Version To Ota Channel    ${node}[ota_channel]    ${artifact}
    Should Be Equal As Integers    ${status}    200

The Node Version Should Be
    [Arguments]    ${uuid}    ${expected}
    ${node}=    Api Get Node By Uuid    ${uuid}
    Should Be Equal    ${node}[version]    ${expected}

The Node Version Should Become
    [Arguments]    ${uuid}    ${expected}
    Wait Until Keyword Succeeds    ${RETRIES}    ${INTERVAL}    Poll And Check Version    ${uuid}    ${expected}

Poll And Check Version
    [Arguments]    ${uuid}    ${expected}
    Api Poll Ota    ${uuid}
    The Node Version Should Be    ${uuid}    ${expected}

The Node Should Report An Error
    [Arguments]    ${uuid}
    Wait Until Keyword Succeeds    ${RETRIES}    ${INTERVAL}    Poll And Check Error    ${uuid}

Poll And Check Error
    [Arguments]    ${uuid}
    Api Poll Ota    ${uuid}
    ${node}=    Api Get Node By Uuid    ${uuid}
    Should Not Be Empty    ${node}[last_error]

The Node Should Have No Error
    [Arguments]    ${uuid}
    ${node}=    Api Get Node By Uuid    ${uuid}
    Should Be Empty    ${node}[last_error]

DFU Is Triggered
    [Arguments]    ${serial}    ${version}
    Api Trigger Dfu    ${serial}    ${version}

The Backlog Is Drained
    [Arguments]    ${serial}
    Api Drain Backlog    ${serial}

The Endpoint Version Should Be
    [Arguments]    ${serial}    ${expected}
    ${ep}=    Api Get Endpoint By Serial    ${serial}
    Should Be Equal    ${ep}[version]    ${expected}