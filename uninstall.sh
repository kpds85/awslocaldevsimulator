RED='\033[0;31m'
NC='\033[0m'
echo "======================================================================"
echo -e "${RED}Tear Down Containers and simulated environment...${NC}"
echo "======================================================================"
docker compose -f infrastructure/docker-compose.yml down
echo -e "${RED}Done! All containers are stopped and removed.${NC}"