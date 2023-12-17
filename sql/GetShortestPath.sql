CREATE PROCEDURE GetShortestPath
    @start VARCHAR(255),
    @destination VARCHAR(255)
AS
WITH searchAlgorithm AS (
    SELECT
        json_value(Devices.$node_id, '$.id') AS startNode,
        device_name AS atNode,
        device_name AS shortestPaths,
        json_value(Conveyers.$edge_id, '$.id') AS edgeID,
        0 AS pathCounter
    FROM
        Devices
        JOIN Conveyers ON json_value(Devices.$node_id, '$.id') = json_value(Conveyers.$from_id, '$.id')
    WHERE
        device_name = @start
        AND is_source = 1
        AND is_active = 1
    UNION
    ALL
    SELECT
        json_value(Conveyers.$to_id, '$.id') AS startNode,
        device_name AS atNode,
        CAST(
            shortestPaths + ',' + device_name AS varchar(8000)
        ) AS shortestPaths,
        json_value(Conveyers.$edge_id, '$.id') AS edgeID,
        pathCounter + Conveyers.cost + Devices.cost AS pathCounter
    FROM
        searchAlgorithm
        JOIN Conveyers ON startNode = json_value(Conveyers.$from_id, '$.id')
        JOIN Devices ON json_value(Conveyers.$to_id, '$.id') = json_value(Devices.$node_id, '$.id')
    WHERE
        ((LEN(shortestPaths) - LEN(atNode) = 0)
        OR (LEN(shortestPaths) - LEN(','+atNode) = LEN(REPLACE(shortestPaths, ','+atNode, ''))))
        AND
        is_active = 1
)
SELECT DISTINCT TOP 5
    shortestPaths,
    pathCounter - (SELECT cost FROM Devices WHERE device_name = atNode) AS pathCost
FROM
    searchAlgorithm
WHERE
    WHERE
    ((LEN(@destination) = 0) AND ((SELECT is_destination FROM Devices WHERE device_name = atNode) = 1))
    OR
    ((LEN(@destination) > 0) AND (atNode IN (SELECT * FROM STRING_SPLIT(@destination, ','))))
ORDER BY
    pathCost;