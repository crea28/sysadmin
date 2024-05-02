#!/bin/bash 
# git-backup.sh
# apt-get install jq
# Create token : https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

TOKEN=""
DIRBACKUP="/backup/github"
REPOPRIVATELIST=('');
REPOPUBLICLIST=('');
TODAY=$(date "+%F")
LOGFILE="/root/scripts/git-backup.log"
ORG=""

# Create backup dir
mkdir -p ${DIRBACKUP}/${TODAY}/archives

# Get private repo url
for page in $(seq 3)
do
    PRIVATEREPO=`curl -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" -sL "https://api.github.com/orgs/${ORG}/repos?type=private&per_page=100&page=${page}" | jq -r ".[].name"`
    REPOPRIVATELIST+=(${PRIVATEREPO})
done

# Get public repo url
for page in $(seq 1)
do
    PUBLICREPO=`curl -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" -sL "https://api.github.com/orgs/${ORG}/repos?type=public&per_page=100&page=${page}" | jq -r ".[].name"`
    REPOPUBLICLIST+=(${PUBLICREPO})
done

# Git clone of all private projects
for repo in ${REPOPRIVATELIST[@]}
do
    dateStart=`date +%Y-%m-%d\ %H:%M:%S`
    echo "${dateStart} - Starting clone private repo" >> ${LOGFILE}
    cd ${DIRBACKUP}/${TODAY}
    git clone "https://${TOKEN}@github.com/${ORG}/${repo}.git"
    tar -zcvf ${DIRBACKUP}/${TODAY}/archives/${repo}-${TODAY}.tar.gz ${DIRBACKUP}/${TODAY}/${repo}/
    rm -rf ${DIRBACKUP}/${TODAY}/${repo}
    dateEnd=`date +%Y-%m-%d\ %H:%M:%S`
    echo "${dateEnd} - Ending clone private repo" >> ${LOGFILE}
done

# Git clone of all public projects
for repo in ${REPOPUBLICLIST[@]}
do
    dateStart=`date +%Y-%m-%d\ %H:%M:%S`
    echo "${dateStart} - Starting clone public repo"  >> ${LOGFILE}
    cd ${DIRBACKUP}/${TODAY}
    git clone "https://${TOKEN}@github.com/${ORG}/${repo}.git"
    tar -zcvf ${DIRBACKUP}/${TODAY}/archives/${repo}-${TODAY}.tar.gz ${DIRBACKUP}/${TODAY}/${repo}/
    rm -rf ${DIRBACKUP}/${TODAY}/${repo}
    dateEnd=`date +%Y-%m-%d\ %H:%M:%S`
    echo "${dateEnd} - Ending clone private repo" >> ${LOGFILE}
done
