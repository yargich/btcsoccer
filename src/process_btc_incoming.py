#!/usr/bin/python

# script will check if money is payed on pending betslips and will move the betslips accordingly


import sys, os, logging
from decimal import Decimal
import simplejson as json

import btcs
import notify_email

import wallet


def process_incoming(betslip):

    recv = wallet.getreceivedby(betslip, 0)

    if recv == 0:
        logging.info('Betslip %s: Nothing received' % (betslip))
        return

    # read betslip
    with open(btcs.path('bets/new', betslip),'r') as f:
        betslip_data = json.loads(f.read())
    
    # Sum total in betslip
    total = Decimal('0')
    for bets in betslip_data['bets']:
        total += Decimal(bets['amount'])

    total = total / Decimal('1000')

    if recv == total:
        logging.info('Betslip %s: Received %s, moving to received' % (betslip, recv))
        
        os.rename(btcs.path('bets/new', betslip), btcs.path('bets/received', betslip))

        # attach game data for email
        if 'email_address' in betslip_data:
            for bet in betslip_data['bets']:
                try:
                    with open(btcs.path('games/new', bet['game']), 'r') as f:
                        bet['game_data'] = json.loads(f.read())

                except Exception:
                    # only for email; do not trip over it
                    pass
            notify_email.sendmail('email_betslip.html', betslip_data, 
                betslip_data['email_address'], 'Betslip payment received')

            


    else:
        logging.warning('Betslip %s: Invalid amount received: %s, expected %s' % (betslip, recv, total))
        logging.warning('Return amount manually')
    



def process_incoming_all():
    logging.info('process-incoming-all started')
    for betslip in os.listdir(btcs.path('bets/new','')):
        process_incoming(betslip)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) != 2:
        print('Pass --all or betslip-address as parameter')
    elif sys.argv[-1] == '--all':
        process_incoming_all()
    else:
        process_incoming(sys.argv[-1])


